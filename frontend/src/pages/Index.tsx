import { useEffect, useMemo, useState } from "react";
import { Shield, Activity, Search, ShieldAlert, Zap } from "lucide-react";

import { ArchitectureDiagram } from "@/components/dashboard/ArchitectureDiagram";
import { DashboardCard } from "@/components/dashboard/DashboardCard";
import { OpenEnvSpec } from "@/components/dashboard/OpenEnvSpec";
import { StatusIndicator } from "@/components/dashboard/StatusIndicator";
import {
  closeScenario,
  demoQuery,
  fetchState,
  healthCheck,
  listTasks,
  resetScenario,
  sendStep,
  type DemoSocResponse,
  type ResponseAction,
  type Severity,
  type SocActionPayload,
  type SocObservation,
  type SocState,
  type SocStepResult,
  type ToolName,
  type ModelTier,
} from "@/lib/api";

const RESPONSE_OPTIONS: ResponseAction[] = [
  "ignore",
  "investigate",
  "request_verification",
  "escalate_to_human",
  "flag_anomaly",
  "block_user",
  "isolate_host",
  "trigger_incident_response",
  "open_incident",
];

const TOOL_OPTIONS: ToolName[] = ["none", "log_analyzer", "identity_verifier", "network_monitor"];
const MODEL_OPTIONS: ModelTier[] = ["cheap", "balanced", "deep"];
const SEVERITY_OPTIONS: Array<Severity | ""> = ["", "medium", "high", "critical"];

const initialAction: SocActionPayload = {
  response_action: "investigate",
  target_alert_id: null,
  tool_name: "none",
  model_tier: "cheap",
  escalate_severity: null,
  reasoning_note: null,
};

const formatTask = (task: string) => task.replaceAll("_", " ");

const Index = () => {
  const [tasks, setTasks] = useState<string[]>([]);
  const [selectedTask, setSelectedTask] = useState("helpdesk_takeover");
  const [seed, setSeed] = useState(7);
  const [action, setAction] = useState<SocActionPayload>(initialAction);
  const [observation, setObservation] = useState<SocObservation | null>(null);
  const [state, setState] = useState<SocState | null>(null);
  const [lastResult, setLastResult] = useState<SocStepResult | null>(null);
  const [demoText, setDemoText] = useState("");
  const [demoResult, setDemoResult] = useState<DemoSocResponse | null>(null);
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);
  const [statusMessage, setStatusMessage] = useState("Connecting to the SOC backend...");
  const [statusError, setStatusError] = useState(false);
  const [logEntries, setLogEntries] = useState<Array<{ title: string; payload: unknown }>>([]);

  useEffect(() => {
    async function bootstrap() {
      try {
        await healthCheck();
        setApiOnline(true);
        const taskPayload = await listTasks();
        setTasks(taskPayload.tasks);
        if (taskPayload.tasks.length > 0) setSelectedTask(taskPayload.tasks[0]);
        setStatusMessage("Backend connected. Reset a scenario or route a demo query.");
        setStatusError(false);
      } catch (error) {
        setApiOnline(false);
        setStatusMessage(error instanceof Error ? error.message : "Could not connect to backend.");
        setStatusError(true);
      }
    }
    void bootstrap();
  }, []);

  const metrics = useMemo(() => {
    if (!observation || !state) return [];
    return [
      ["task", formatTask(observation.task_name)],
      ["step", `${observation.step_index}/${observation.max_steps}`],
      ["risk", observation.system_risk_level.toFixed(3)],
      ["progression", observation.attacker_progression_score.toFixed(3)],
      ["compute budget", observation.remaining_compute_budget.toFixed(2)],
      ["latency budget", `${observation.remaining_latency_budget_ms} ms`],
      ["incident", observation.incident_open ? `open (${observation.incident_severity ?? "n/a"})` : "closed"],
      ["final score", state.final_score.toFixed(3)],
      ["breach prevented", state.breach_prevented ? "yes" : "no"],
      ["breach occurred", state.breach_occurred ? "yes" : "no"],
    ];
  }, [observation, state]);

  function addLog(title: string, payload: unknown) {
    setLogEntries((prev) => [{ title, payload }, ...prev].slice(0, 10));
  }

  function setStatus(message: string, error = false) {
    setStatusMessage(message);
    setStatusError(error);
  }

  async function refreshStatePanel() {
    try {
      const statePayload = await fetchState();
      setState(statePayload);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Could not refresh state.", true);
    }
  }

  async function handleReset() {
    try {
      const result = await resetScenario(selectedTask, seed);
      setObservation(result.observation);
      setLastResult(result);
      setAction((current) => ({
        ...current,
        target_alert_id: result.observation.visible_alerts.at(-1)?.alert_id ?? null,
      }));
      addLog("reset", result);
      setStatus(`Scenario reset for ${formatTask(selectedTask)}.`);
      await refreshStatePanel();
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Reset failed.", true);
    }
  }

  async function handleStep() {
    try {
      const result = await sendStep(action);
      setObservation(result.observation);
      setLastResult(result);
      setAction((current) => ({
        ...current,
        target_alert_id: result.observation.visible_alerts.at(-1)?.alert_id ?? current.target_alert_id,
      }));
      addLog("step", { action, result });
      setStatus(
        `Reward ${result.reward.toFixed(3)} | grader ${result.info.grader_score.toFixed(3)} | done=${result.done}`
      );
      await refreshStatePanel();
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Step failed.", true);
    }
  }

  async function handleClose() {
    try {
      await closeScenario();
      setObservation(null);
      setState(null);
      setLastResult(null);
      addLog("close", { status: "closed" });
      setStatus("Episode closed.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Close failed.", true);
    }
  }

  async function handleDemoRoute() {
    try {
      if (!demoText.trim()) {
        throw new Error("Enter a demo query first.");
      }
      const result = await demoQuery(demoText);
      setDemoResult(result);
      setAction(result.decision.action);
      if (result.suggested_task) setSelectedTask(result.suggested_task);
      addLog("demo_query", result);
      setStatus(
        `Demo routed to ${formatTask(result.suggested_task)} using ${result.decision.action.model_tier}.`
      );
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Demo route failed.", true);
    }
  }

  return (
    <div className="min-h-screen bg-background p-4 md:p-6 space-y-6">
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-primary/10 border border-primary/30 flex items-center justify-center border-glow-cyan">
            <Shield className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-foreground tracking-tight">
              <span className="text-glow-cyan">Sentinel Shield</span> — SOC Guardian
            </h1>
            <p className="text-xs text-muted-foreground font-mono">
              Live incident triage with tool selection, model routing, and OpenEnv-backed attack simulation
            </p>
          </div>
        </div>
        <div className="flex items-center gap-4 flex-wrap">
          <StatusIndicator status={apiOnline ? "online" : apiOnline === false ? "critical" : "warning"} label="API" />
          <StatusIndicator status="online" label="OpenEnv Core" />
          <StatusIndicator status={state?.incident_open ? "warning" : "online"} label="Incident" />
          <StatusIndicator status={state?.breach_occurred ? "critical" : "online"} label="Outcome" />
        </div>
      </header>

      <ArchitectureDiagram />

      <div className={`rounded-lg border px-4 py-3 text-sm font-mono ${statusError ? "border-destructive/40 bg-destructive/10 text-destructive" : "border-primary/30 bg-primary/10 text-primary"}`}>
        {statusMessage}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-4">
        <div className="xl:col-span-4 space-y-4">
          <DashboardCard title="Scenario Control" subtitle="Live Backend" variant="cyan">
            <div className="space-y-3">
              <label className="text-xs font-mono text-muted-foreground">
                Task
                <select
                  value={selectedTask}
                  onChange={(e) => setSelectedTask(e.target.value)}
                  className="mt-1 w-full rounded bg-secondary border border-border px-3 py-2 text-sm"
                >
                  {tasks.map((task) => (
                    <option key={task} value={task}>
                      {formatTask(task)}
                    </option>
                  ))}
                </select>
              </label>
              <label className="text-xs font-mono text-muted-foreground">
                Seed
                <input
                  type="number"
                  value={seed}
                  onChange={(e) => setSeed(Number(e.target.value))}
                  className="mt-1 w-full rounded bg-secondary border border-border px-3 py-2 text-sm"
                />
              </label>
              <div className="flex gap-2">
                <button onClick={handleReset} className="flex-1 rounded bg-primary px-3 py-2 text-xs font-mono font-bold text-primary-foreground">
                  Reset
                </button>
                <button onClick={refreshStatePanel} className="flex-1 rounded bg-secondary px-3 py-2 text-xs font-mono">
                  Refresh State
                </button>
              </div>
            </div>
          </DashboardCard>

          <DashboardCard title="Decision Engine" subtitle="Manual Step Control" variant="purple">
            <div className="space-y-3">
              <label className="text-xs font-mono text-muted-foreground">
                Response Action
                <select
                  value={action.response_action}
                  onChange={(e) => setAction((current) => ({ ...current, response_action: e.target.value as ResponseAction }))}
                  className="mt-1 w-full rounded bg-secondary border border-border px-3 py-2 text-sm"
                >
                  {RESPONSE_OPTIONS.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              </label>
              <label className="text-xs font-mono text-muted-foreground">
                Target Alert Id
                <input
                  value={action.target_alert_id ?? ""}
                  onChange={(e) => setAction((current) => ({ ...current, target_alert_id: e.target.value || null }))}
                  className="mt-1 w-full rounded bg-secondary border border-border px-3 py-2 text-sm"
                  placeholder="alert id"
                />
              </label>
              <label className="text-xs font-mono text-muted-foreground">
                Tool
                <select
                  value={action.tool_name}
                  onChange={(e) => setAction((current) => ({ ...current, tool_name: e.target.value as ToolName }))}
                  className="mt-1 w-full rounded bg-secondary border border-border px-3 py-2 text-sm"
                >
                  {TOOL_OPTIONS.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              </label>
              <label className="text-xs font-mono text-muted-foreground">
                Model Tier
                <select
                  value={action.model_tier}
                  onChange={(e) => setAction((current) => ({ ...current, model_tier: e.target.value as ModelTier }))}
                  className="mt-1 w-full rounded bg-secondary border border-border px-3 py-2 text-sm"
                >
                  {MODEL_OPTIONS.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              </label>
              <label className="text-xs font-mono text-muted-foreground">
                Escalate Severity
                <select
                  value={action.escalate_severity ?? ""}
                  onChange={(e) =>
                    setAction((current) => ({
                      ...current,
                      escalate_severity: (e.target.value || null) as Severity | null,
                    }))
                  }
                  className="mt-1 w-full rounded bg-secondary border border-border px-3 py-2 text-sm"
                >
                  {SEVERITY_OPTIONS.map((option) => (
                    <option key={option || "none"} value={option}>
                      {option || "none"}
                    </option>
                  ))}
                </select>
              </label>
              <label className="text-xs font-mono text-muted-foreground">
                Reasoning Note
                <textarea
                  value={action.reasoning_note ?? ""}
                  onChange={(e) => setAction((current) => ({ ...current, reasoning_note: e.target.value || null }))}
                  className="mt-1 min-h-[90px] w-full rounded bg-secondary border border-border px-3 py-2 text-sm"
                  placeholder="Why this action?"
                />
              </label>
              <div className="flex gap-2">
                <button onClick={handleStep} className="flex-1 rounded bg-accent px-3 py-2 text-xs font-mono font-bold text-accent-foreground">
                  Send Step
                </button>
                <button onClick={handleClose} className="flex-1 rounded bg-destructive px-3 py-2 text-xs font-mono font-bold text-destructive-foreground">
                  Close
                </button>
              </div>
            </div>
          </DashboardCard>

          <DashboardCard title="Quick Demo Query" subtitle="Real Usability Layer" variant="default">
            <div className="space-y-3">
              <textarea
                value={demoText}
                onChange={(e) => setDemoText(e.target.value)}
                className="min-h-[110px] w-full rounded bg-secondary border border-border px-3 py-2 text-sm"
                placeholder="Example: Caller failed identity checks and then logged in from an unfamiliar location."
              />
              <button onClick={handleDemoRoute} className="w-full rounded bg-secondary px-3 py-2 text-xs font-mono font-bold">
                Route Demo Query
              </button>
              <pre className="rounded bg-secondary/50 p-3 text-[11px] text-muted-foreground whitespace-pre-wrap">
                {demoResult ? JSON.stringify(demoResult, null, 2) : "No demo route yet."}
              </pre>
            </div>
          </DashboardCard>
        </div>

        <div className="xl:col-span-8 space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { label: "Visible Alerts", value: observation?.visible_alerts.length ?? 0, icon: Activity, color: "text-primary" },
              { label: "Risk Level", value: observation ? observation.system_risk_level.toFixed(3) : "0.000", icon: ShieldAlert, color: "text-warning" },
              { label: "Current Step", value: observation ? `${observation.step_index}/${observation.max_steps}` : "0/0", icon: Search, color: "text-info" },
              { label: "Final Score", value: state ? state.final_score.toFixed(3) : "0.000", icon: Zap, color: "text-success" },
            ].map((metric) => (
              <div key={metric.label} className="bg-card rounded-lg border border-border p-4">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-[10px] uppercase tracking-widest text-muted-foreground font-mono">{metric.label}</span>
                  <metric.icon className={`h-4 w-4 ${metric.color}`} />
                </div>
                <div className={`text-2xl font-bold font-mono ${metric.color}`}>{metric.value}</div>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <DashboardCard title="Visible Alerts" subtitle="Agent Observation" variant="cyan">
              <div className="space-y-2 max-h-[360px] overflow-auto">
                {observation?.visible_alerts?.length ? observation.visible_alerts.map((alert) => (
                  <div key={alert.alert_id} className="rounded bg-secondary/50 border border-border p-3">
                    <div className="flex items-center justify-between gap-2">
                      <div className="text-sm font-semibold">{alert.title}</div>
                      <span className="text-[10px] font-mono uppercase text-muted-foreground">{alert.severity}</span>
                    </div>
                    <div className="mt-1 text-xs text-muted-foreground">{alert.description}</div>
                    <div className="mt-2 flex flex-wrap gap-2">
                      <span className="rounded bg-background/80 px-2 py-1 text-[10px] font-mono">{alert.alert_id}</span>
                      <span className="rounded bg-background/80 px-2 py-1 text-[10px] font-mono">{alert.source}</span>
                      <span className="rounded bg-background/80 px-2 py-1 text-[10px] font-mono">signal={alert.signal_strength}</span>
                      {alert.tags.map((tag) => (
                        <span key={tag} className="rounded bg-primary/10 px-2 py-1 text-[10px] font-mono text-primary">{tag}</span>
                      ))}
                    </div>
                  </div>
                )) : (
                  <div className="text-sm text-muted-foreground">No alerts loaded. Reset a scenario to begin.</div>
                )}
              </div>
            </DashboardCard>

            <DashboardCard title="Metrics & State" subtitle="Live Environment" variant="purple">
              <div className="grid grid-cols-[140px_1fr] gap-x-3 gap-y-2 text-sm">
                {metrics.length ? metrics.map(([label, value]) => (
                  <FragmentRow key={label} label={label} value={value} />
                )) : <div className="col-span-2 text-sm text-muted-foreground">No state loaded yet.</div>}
              </div>
              <div className="mt-4 pt-4 border-t border-border">
                <div className="text-xs uppercase tracking-widest text-muted-foreground font-mono mb-2">Analyst Notes</div>
                <div className="flex flex-wrap gap-2">
                  {observation?.analyst_notes?.length ? observation.analyst_notes.map((note) => (
                    <span key={note} className="rounded-full border border-primary/20 bg-primary/10 px-3 py-1 text-xs text-primary">
                      {note}
                    </span>
                  )) : <span className="text-sm text-muted-foreground">No notes yet.</span>}
                </div>
              </div>
            </DashboardCard>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <DashboardCard title="Latest Step Result" subtitle="Reward / Penalties" variant="default">
              <pre className="max-h-[360px] overflow-auto text-xs text-muted-foreground">
                {lastResult ? JSON.stringify(lastResult, null, 2) : "No step executed yet."}
              </pre>
            </DashboardCard>
            <DashboardCard title="State Snapshot" subtitle="Debug View" variant="default">
              <pre className="max-h-[360px] overflow-auto text-xs text-muted-foreground">
                {state ? JSON.stringify(state, null, 2) : "No state loaded yet."}
              </pre>
            </DashboardCard>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <OpenEnvSpec />
            <DashboardCard title="Action Log" subtitle="Recent Requests" variant="default">
              <div className="space-y-2 max-h-[320px] overflow-auto">
                {logEntries.length ? logEntries.map((entry, idx) => (
                  <div key={`${entry.title}-${idx}`} className="rounded border border-border bg-secondary/50 p-3">
                    <div className="mb-2 text-xs font-mono uppercase tracking-wider text-muted-foreground">{entry.title}</div>
                    <pre className="text-[11px] text-muted-foreground whitespace-pre-wrap">
                      {JSON.stringify(entry.payload, null, 2)}
                    </pre>
                  </div>
                )) : (
                  <div className="text-sm text-muted-foreground">No actions yet.</div>
                )}
              </div>
            </DashboardCard>
          </div>
        </div>
      </div>
    </div>
  );
};

function FragmentRow({ label, value }: { label: string; value: string }) {
  return (
    <>
      <div className="text-muted-foreground">{label}</div>
      <div className="font-mono text-foreground">{value}</div>
    </>
  );
}

export default Index;
