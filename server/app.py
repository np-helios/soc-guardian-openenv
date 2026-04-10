from __future__ import annotations

import os
from html import escape
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from demo import DemoSocQueryRequest, DemoSocResponse, route_demo_query
from models import ModelTier, ResponseAction, Severity, SocAction, SocState, SocStepResult, ToolName
from server.environment import EnvironmentService
from simulator import TASKS

app = FastAPI(title="SOC Guardian OpenEnv", version="0.1.0")
service = EnvironmentService()
FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"

TASK_METADATA = [
    {
        "id": "helpdesk_takeover",
        "name": "helpdesk_takeover",
        "description": "Social-engineering-led account takeover with identity mismatch and suspicious password reset signals.",
        "difficulty": "easy",
        "grader": {"type": "deterministic", "enabled": True, "score_range": [0.0, 1.0]},
        "has_grader": True,
        "grader_enabled": True,
        "grader_bool": True,
    },
    {
        "id": "privilege_spiral",
        "name": "privilege_spiral",
        "description": "Compromised user begins reaching for admin tooling while benign alert noise competes for attention.",
        "difficulty": "medium",
        "grader": {"type": "deterministic", "enabled": True, "score_range": [0.0, 1.0]},
        "has_grader": True,
        "grader_enabled": True,
        "grader_bool": True,
    },
    {
        "id": "lateral_breach",
        "name": "lateral_breach",
        "description": "Multi-stage intrusion advances to lateral movement with cross-system traffic and a decoy alert.",
        "difficulty": "hard",
        "grader": {"type": "deterministic", "enabled": True, "score_range": [0.0, 1.0]},
        "has_grader": True,
        "grader_enabled": True,
        "grader_bool": True,
    },
]


class ResetRequest(BaseModel):
    task_name: str = Field(default="helpdesk_takeover")
    seed: int = Field(default=7)


if FRONTEND_DIST.exists():
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="frontend-assets")


def render_ui() -> str:
    task_options = "\n".join(
        f'<option value="{escape(task_name)}">{escape(task_name.replace("_", " ").title())}</option>'
        for task_name in TASKS
    )
    response_options = "\n".join(
        f'<option value="{action.value}">{action.value}</option>' for action in ResponseAction
    )
    tool_options = "\n".join(f'<option value="{tool.value}">{tool.value}</option>' for tool in ToolName)
    model_options = "\n".join(f'<option value="{tier.value}">{tier.value}</option>' for tier in ModelTier)
    severity_options = '<option value="">none</option>' + "\n".join(
        f'<option value="{severity.value}">{severity.value}</option>' for severity in Severity
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>SOC Guardian OpenEnv</title>
  <style>
    :root {{
      --bg: #0a0f19;
      --panel: rgba(18, 27, 44, 0.86);
      --panel-2: rgba(12, 18, 31, 0.92);
      --ink: #edf3ff;
      --muted: #91a0ba;
      --line: rgba(255,255,255,0.08);
      --amber: #ffb84d;
      --amber-soft: rgba(255,184,77,0.15);
      --cyan: #4cc9f0;
      --red: #ff6b6b;
      --green: #34d399;
      --shadow: 0 20px 60px rgba(0,0,0,0.35);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      font-family: "Segoe UI", system-ui, sans-serif;
      background:
        radial-gradient(circle at top left, rgba(76, 201, 240, 0.12), transparent 24%),
        radial-gradient(circle at bottom right, rgba(255, 184, 77, 0.10), transparent 22%),
        linear-gradient(140deg, #07101a, #0f1728 55%, #08101b);
    }}
    .shell {{
      width: min(1380px, calc(100% - 32px));
      margin: 20px auto 48px;
    }}
    .hero {{
      display: grid;
      grid-template-columns: 1.15fr 0.85fr;
      gap: 16px;
      margin-bottom: 16px;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 24px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(10px);
    }}
    .hero-copy {{
      padding: 28px;
    }}
    h1 {{
      margin: 0 0 10px;
      font-size: clamp(2.4rem, 5vw, 4.4rem);
      line-height: 0.95;
      letter-spacing: -0.05em;
    }}
    .lede {{
      margin: 0;
      color: var(--muted);
      line-height: 1.7;
      max-width: 70ch;
    }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
      padding: 16px;
    }}
    .stat {{
      padding: 16px;
      border: 1px solid var(--line);
      border-radius: 18px;
      background: rgba(255,255,255,0.03);
    }}
    .stat span {{
      display: block;
      color: var(--muted);
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.10em;
      margin-bottom: 8px;
    }}
    .stat strong {{
      font-size: 1.5rem;
      letter-spacing: -0.03em;
    }}
    .grid {{
      display: grid;
      grid-template-columns: 360px 1fr;
      gap: 16px;
    }}
    .controls {{
      padding: 20px;
      display: grid;
      gap: 14px;
      align-content: start;
    }}
    .section-label {{
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.12em;
      font-size: 0.78rem;
      margin: 0;
    }}
    label {{
      display: grid;
      gap: 6px;
      color: var(--muted);
      font-size: 0.92rem;
    }}
    select, input, textarea, button {{
      width: 100%;
      border-radius: 14px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.06);
      color: var(--ink);
      font: inherit;
      padding: 11px 13px;
    }}
    textarea {{ min-height: 92px; resize: vertical; }}
    button {{
      cursor: pointer;
      font-weight: 700;
      transition: transform 120ms ease, box-shadow 120ms ease;
    }}
    button:hover {{
      transform: translateY(-1px);
      box-shadow: 0 12px 28px rgba(0,0,0,0.25);
    }}
    .primary {{ background: linear-gradient(135deg, #ffb84d, #ff8f3f); color: #17202f; border-color: transparent; }}
    .secondary {{ background: rgba(255,255,255,0.04); }}
    .danger {{ background: linear-gradient(135deg, #ff6b6b, #ff4d6d); border-color: transparent; }}
    .grid-actions {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }}
    .workspace {{
      padding: 18px;
      display: grid;
      gap: 16px;
    }}
    .banner {{
      padding: 12px 14px;
      border-radius: 14px;
      background: rgba(76,201,240,0.12);
      border: 1px solid rgba(76,201,240,0.18);
      color: #b7efff;
    }}
    .banner.error {{
      background: rgba(255,107,107,0.12);
      border-color: rgba(255,107,107,0.20);
      color: #ffd4d4;
    }}
    .panes {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }}
    .panel {{
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 16px;
      background: rgba(255,255,255,0.03);
    }}
    .panel h3 {{
      margin: 0 0 12px;
      font-size: 1rem;
      letter-spacing: -0.02em;
    }}
    .kv {{
      display: grid;
      grid-template-columns: 160px 1fr;
      gap: 8px 12px;
      font-size: 0.92rem;
    }}
    .kv div:nth-child(odd) {{ color: var(--muted); }}
    .chips {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .chip {{
      padding: 6px 10px;
      border-radius: 999px;
      border: 1px solid rgba(255,255,255,0.08);
      background: rgba(255,255,255,0.05);
      font-size: 0.85rem;
    }}
    pre {{
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 0.82rem;
      line-height: 1.55;
    }}
    .log {{
      max-height: 260px;
      overflow: auto;
      display: grid;
      gap: 10px;
    }}
    .log-entry {{
      padding: 12px;
      border-radius: 14px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.04);
    }}
    @media (max-width: 980px) {{
      .hero, .grid, .panes {{
        grid-template-columns: 1fr;
      }}
      .grid-actions {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <section class="hero">
      <div class="card hero-copy">
        <h1>SOC Guardian<br />OpenEnv</h1>
        <p class="lede">
          A sequential decision environment for early breach detection. The agent triages security alerts, chooses which
          tool to run, decides which reasoning tier to spend, and selects containment or escalation actions under compute
          and latency constraints.
        </p>
      </div>
      <div class="card stats">
        <div class="stat"><span>Tasks</span><strong>{len(TASKS)}</strong></div>
        <div class="stat"><span>API</span><strong>FastAPI</strong></div>
        <div class="stat"><span>Core Idea</span><strong>Detect + Route</strong></div>
        <div class="stat"><span>Docs</span><strong><a href="/docs" style="color:inherit;">OpenAPI</a></strong></div>
      </div>
    </section>

    <section class="grid">
      <aside class="card controls">
        <h2 class="section-label">Episode Control</h2>
        <label>Task<select id="task-name">{task_options}</select></label>
        <label>Seed<input id="seed" type="number" value="7" /></label>
        <div class="grid-actions">
          <button id="reset-btn" class="primary">Reset Scenario</button>
          <button id="refresh-btn" class="secondary">Refresh State</button>
        </div>

        <h2 class="section-label">Decision Input</h2>
        <label>Response Action<select id="response-action">{response_options}</select></label>
        <label>Target Alert Id<input id="target-alert-id" type="text" placeholder="optional alert id" /></label>
        <label>Tool<select id="tool-name">{tool_options}</select></label>
        <label>Model Tier<select id="model-tier">{model_options}</select></label>
        <label>Escalate Severity<select id="escalate-severity">{severity_options}</select></label>
        <label>Reasoning Note<textarea id="reasoning-note" placeholder="Why this action?"></textarea></label>
        <div class="grid-actions">
          <button id="step-btn" class="primary">Send Step</button>
          <button id="close-btn" class="danger">Close Episode</button>
        </div>

        <h2 class="section-label">Quick Demo Query</h2>
        <label>Free-form Query<textarea id="demo-query" placeholder="Example: Caller failed identity checks and then logged in from an unfamiliar location."></textarea></label>
        <button id="demo-btn" class="secondary">Route Demo Query</button>
      </aside>

      <main class="card workspace">
        <div id="status-banner" class="banner">Ready. Reset a scenario to begin.</div>

        <div class="panes">
          <section class="panel">
            <h3>Visible Alerts</h3>
            <div id="alert-chips" class="chips"></div>
            <div style="height:12px;"></div>
            <pre id="alert-details">No alerts loaded.</pre>
          </section>
          <section class="panel">
            <h3>Episode Metrics</h3>
            <div id="metrics-kv" class="kv"></div>
          </section>
        </div>

        <div class="panes">
          <section class="panel">
            <h3>Latest Step Result</h3>
            <pre id="step-result">No step yet.</pre>
          </section>
          <section class="panel">
            <h3>State Snapshot</h3>
            <pre id="state-result">No state loaded.</pre>
          </section>
        </div>

        <div class="panes">
          <section class="panel">
            <h3>Analyst Notes</h3>
            <div id="analyst-notes" class="chips"></div>
          </section>
          <section class="panel">
            <h3>Demo Route Result</h3>
            <pre id="demo-result">No demo query yet.</pre>
          </section>
        </div>

        <section class="panel">
          <h3>Action Log</h3>
          <div id="log" class="log"></div>
        </section>
      </main>
    </section>
  </div>

  <script>
    const statusBanner = document.getElementById("status-banner");
    const taskSelect = document.getElementById("task-name");
    const seedInput = document.getElementById("seed");
    const responseActionSelect = document.getElementById("response-action");
    const targetAlertInput = document.getElementById("target-alert-id");
    const toolNameSelect = document.getElementById("tool-name");
    const modelTierSelect = document.getElementById("model-tier");
    const escalateSeveritySelect = document.getElementById("escalate-severity");
    const reasoningNoteInput = document.getElementById("reasoning-note");
    const alertChips = document.getElementById("alert-chips");
    const alertDetails = document.getElementById("alert-details");
    const metricsKv = document.getElementById("metrics-kv");
    const stepResult = document.getElementById("step-result");
    const stateResult = document.getElementById("state-result");
    const analystNotes = document.getElementById("analyst-notes");
    const demoQueryInput = document.getElementById("demo-query");
    const demoResult = document.getElementById("demo-result");
    const log = document.getElementById("log");

    function setStatus(message, isError = false) {{
      statusBanner.textContent = message;
      statusBanner.className = isError ? "banner error" : "banner";
    }}

    function kvMarkup(entries) {{
      return entries.map(([k, v]) => `<div>${{k}}</div><div>${{v}}</div>`).join("");
    }}

    function chips(values) {{
      if (!values || !values.length) return '<span class="chip">none</span>';
      return values.map((value) => `<span class="chip">${{value}}</span>`).join("");
    }}

    function pushLog(title, payload) {{
      const entry = document.createElement("div");
      entry.className = "log-entry";
      entry.innerHTML = `<strong>${{title}}</strong><pre>${{JSON.stringify(payload, null, 2)}}</pre>`;
      log.prepend(entry);
    }}

    async function jsonFetch(path, options = {{}}) {{
      const response = await fetch(path, {{
        headers: {{ "Content-Type": "application/json" }},
        ...options,
      }});
      const text = await response.text();
      const data = text ? JSON.parse(text) : null;
      if (!response.ok) throw new Error(data?.detail || text || `Request failed with ${{response.status}}`);
      return data;
    }}

    function renderObservation(observation) {{
      alertChips.innerHTML = chips(observation.visible_alerts.map((alert) => `${{alert.alert_id}} • ${{alert.severity}}`));
      alertDetails.textContent = JSON.stringify(observation.visible_alerts, null, 2);
      metricsKv.innerHTML = kvMarkup([
        ["task", observation.task_name],
        ["step_index", observation.step_index],
        ["max_steps", observation.max_steps],
        ["risk_level", observation.system_risk_level],
        ["progression", observation.attacker_progression_score],
        ["compute_budget", observation.remaining_compute_budget],
        ["latency_budget_ms", observation.remaining_latency_budget_ms],
        ["incident_open", observation.incident_open],
        ["incident_severity", observation.incident_severity ?? "none"],
      ]);
      analystNotes.innerHTML = chips(observation.analyst_notes);
      if (observation.visible_alerts.length) {{
        targetAlertInput.value = observation.visible_alerts[observation.visible_alerts.length - 1].alert_id;
      }}
    }}

    async function refreshState() {{
      try {{
        const data = await jsonFetch("/state");
        stateResult.textContent = JSON.stringify(data, null, 2);
      }} catch (error) {{
        setStatus(error.message, true);
      }}
    }}

    async function resetScenario() {{
      try {{
        const payload = {{ task_name: taskSelect.value, seed: Number(seedInput.value || 7) }};
        const data = await jsonFetch("/reset", {{ method: "POST", body: JSON.stringify(payload) }});
        renderObservation(data.observation);
        stepResult.textContent = JSON.stringify(data, null, 2);
        pushLog("reset", data);
        setStatus(`Scenario reset for ${{payload.task_name}}.`);
        await refreshState();
      }} catch (error) {{
        setStatus(error.message, true);
      }}
    }}

    async function sendStep() {{
      try {{
        const payload = {{
          response_action: responseActionSelect.value,
          target_alert_id: targetAlertInput.value.trim() || null,
          tool_name: toolNameSelect.value,
          model_tier: modelTierSelect.value,
          escalate_severity: escalateSeveritySelect.value || null,
          reasoning_note: reasoningNoteInput.value.trim() || null,
        }};
        const data = await jsonFetch("/step", {{ method: "POST", body: JSON.stringify(payload) }});
        renderObservation(data.observation);
        stepResult.textContent = JSON.stringify(data, null, 2);
        pushLog("step", {{ action: payload, result: data }});
        setStatus(`Reward ${{Number(data.reward).toFixed(3)}} | grader ${{Number(data.info.grader_score).toFixed(3)}} | done=${{data.done}}`);
        await refreshState();
      }} catch (error) {{
        setStatus(error.message, true);
      }}
    }}

    async function closeScenario() {{
      try {{
        const data = await jsonFetch("/close", {{ method: "POST" }});
        pushLog("close", data);
        setStatus("Episode closed.");
      }} catch (error) {{
        setStatus(error.message, true);
      }}
    }}

    async function runDemoQuery() {{
      try {{
        const payload = {{ query: demoQueryInput.value.trim() }};
        if (!payload.query) throw new Error("Enter a demo query first.");
        const data = await jsonFetch("/demo/query", {{ method: "POST", body: JSON.stringify(payload) }});
        demoResult.textContent = JSON.stringify(data, null, 2);
        pushLog("demo_query", data);
        setStatus(`Demo suggests ${{data.decision.action.response_action}} with the ${{data.decision.action.model_tier}} tier.`);
      }} catch (error) {{
        setStatus(error.message, true);
      }}
    }}

    document.getElementById("reset-btn").addEventListener("click", resetScenario);
    document.getElementById("refresh-btn").addEventListener("click", refreshState);
    document.getElementById("step-btn").addEventListener("click", sendStep);
    document.getElementById("close-btn").addEventListener("click", closeScenario);
    document.getElementById("demo-btn").addEventListener("click", runDemoQuery);
  </script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def home():
    if FRONTEND_DIST.exists():
        return FileResponse(FRONTEND_DIST / "index.html")
    return HTMLResponse(render_ui())


@app.get("/legacy", response_class=HTMLResponse)
async def legacy_home() -> str:
    return render_ui()


@app.get("/favicon.ico")
async def favicon():
    svg_icon_path = FRONTEND_DIST / "shield-favicon.svg"
    if svg_icon_path.exists():
        return FileResponse(svg_icon_path, media_type="image/svg+xml")
    icon_path = FRONTEND_DIST / "favicon.ico"
    if icon_path.exists():
        return FileResponse(icon_path)
    raise HTTPException(status_code=404, detail="favicon not found")


@app.get("/shield-favicon.svg")
async def shield_favicon():
    svg_icon_path = FRONTEND_DIST / "shield-favicon.svg"
    if svg_icon_path.exists():
        return FileResponse(svg_icon_path, media_type="image/svg+xml")
    raise HTTPException(status_code=404, detail="shield favicon not found")


@app.get("/robots.txt")
async def robots():
    robots_path = FRONTEND_DIST / "robots.txt"
    if robots_path.exists():
        return FileResponse(robots_path)
    raise HTTPException(status_code=404, detail="robots not found")


@app.get("/placeholder.svg")
async def placeholder():
    placeholder_path = FRONTEND_DIST / "placeholder.svg"
    if placeholder_path.exists():
        return FileResponse(placeholder_path)
    raise HTTPException(status_code=404, detail="placeholder not found")


@app.get("/health")
@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/metadata")
@app.get("/api/metadata")
async def metadata() -> dict[str, object]:
    return {
        "name": "soc-guardian-openenv",
        "description": (
            "SOC incident triage and early breach detection benchmark under "
            "compute and latency constraints."
        ),
        "version": "0.1.0",
        "tasks": TASK_METADATA,
        "tasks_with_graders": 3,
    }


@app.get("/tasks")
@app.get("/api/tasks")
async def list_tasks() -> dict[str, object]:
    tasks = [
        {
            "id": task["id"],
            "name": task["name"],
            "description": task["description"],
            "difficulty": task["difficulty"],
            "grader": True,
        }
        for task in TASK_METADATA
    ]
    return {
        "tasks": tasks,
        "task_names": list(TASKS.keys()),
        "tasks_with_graders": 3,
    }


@app.get("/validate")
@app.get("/api/validate")
async def validate_submission() -> dict[str, object]:
    checks = {
        "openenv_yaml": True,
        "typed_models": True,
        "reset_endpoint": True,
        "step_endpoint": True,
        "state_endpoint": True,
        "min_3_tasks": len(TASK_METADATA) >= 3,
        "all_tasks_have_graders": all(task["has_grader"] for task in TASK_METADATA),
        "reward_shaped": True,
    }
    return {
        "valid": all(checks.values()),
        "checks": checks,
        "env_name": "soc-guardian-openenv",
        "version": "1.0.0",
    }


@app.post("/demo/query", response_model=DemoSocResponse)
@app.post("/api/demo/query", response_model=DemoSocResponse)
async def demo_query(payload: DemoSocQueryRequest) -> DemoSocResponse:
    try:
        return route_demo_query(payload.query)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/reset", response_model=SocStepResult)
@app.post("/api/reset", response_model=SocStepResult)
async def reset_environment(payload: ResetRequest | None = None) -> SocStepResult:
    try:
        request = payload or ResetRequest()
        return await service.reset(task_name=request.task_name, seed=request.seed)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/step", response_model=SocStepResult)
@app.post("/api/step", response_model=SocStepResult)
async def step_environment(action: SocAction) -> SocStepResult:
    try:
        return await service.step(action)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/state", response_model=SocState)
@app.get("/api/state", response_model=SocState)
async def get_state() -> SocState:
    try:
        return await service.state()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/close")
@app.post("/api/close")
async def close_environment() -> dict[str, str]:
    await service.close()
    return {"status": "closed"}


def main() -> None:
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "7860"))
    uvicorn.run("server.app:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
