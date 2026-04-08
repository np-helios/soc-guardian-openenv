from __future__ import annotations

import asyncio
import os
import textwrap
from typing import List, Optional

from openai import OpenAI

from models import ModelTier, ResponseAction, Severity, SocAction, ToolName
from simulator import SocGuardianEnv

IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME") or os.getenv("IMAGE_NAME")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY", "demo-key")
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
TASK_NAME = os.getenv("SOC_GUARDIAN_TASK", "helpdesk_takeover")
BENCHMARK = os.getenv("SOC_GUARDIAN_BENCHMARK", "soc_guardian")
MAX_STEPS = 12
SUCCESS_SCORE_THRESHOLD = 0.60

SYSTEM_PROMPT = textwrap.dedent(
    """
    You are a SOC decision engine. Review visible alerts, choose exactly one response action,
    one optional tool, and one model tier. Reply in this exact pipe-separated format:
    response_action|target_alert_id_or_none|tool_name|model_tier|escalate_severity_or_none
    """
).strip()


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={error if error else 'null'}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}",
        flush=True,
    )


def heuristic_action(observation) -> SocAction:
    alerts = observation.visible_alerts
    latest = alerts[-1]
    if "verification" in " ".join(latest.tags) or "helpdesk" in latest.source:
        return SocAction(
            response_action=ResponseAction.REQUEST_VERIFICATION,
            target_alert_id=latest.alert_id,
            tool_name=ToolName.IDENTITY_VERIFIER,
            model_tier=ModelTier.BALANCED,
            escalate_severity=Severity.HIGH,
        )
    if latest.severity.value == "critical" or "lateral-movement" in latest.tags:
        return SocAction(
            response_action=ResponseAction.TRIGGER_INCIDENT_RESPONSE,
            target_alert_id=latest.alert_id,
            tool_name=ToolName.NETWORK_MONITOR,
            model_tier=ModelTier.DEEP,
            escalate_severity=Severity.CRITICAL,
        )
    if "admin-tools" in latest.tags or "scope-drift" in latest.tags:
        return SocAction(
            response_action=ResponseAction.ISOLATE_HOST,
            target_alert_id=latest.alert_id,
            tool_name=ToolName.LOG_ANALYZER,
            model_tier=ModelTier.DEEP,
            escalate_severity=Severity.HIGH,
        )
    if latest.signal_strength > 0.7:
        return SocAction(
            response_action=ResponseAction.OPEN_INCIDENT,
            target_alert_id=latest.alert_id,
            tool_name=ToolName.LOG_ANALYZER,
            model_tier=ModelTier.BALANCED,
            escalate_severity=Severity.HIGH,
        )
    return SocAction(
        response_action=ResponseAction.INVESTIGATE,
        target_alert_id=latest.alert_id,
        tool_name=ToolName.LOG_ANALYZER,
        model_tier=ModelTier.CHEAP,
        escalate_severity=Severity.MEDIUM,
    )


def prompt_for_model(observation) -> str:
    alerts = "\n".join(
        f"{alert.alert_id}: severity={alert.severity.value} source={alert.source} tags={','.join(alert.tags)} signal={alert.signal_strength}"
        for alert in observation.visible_alerts
    )
    return textwrap.dedent(
        f"""
        task={observation.task_name}
        step_index={observation.step_index}
        risk={observation.system_risk_level}
        progression={observation.attacker_progression_score}
        remaining_compute_budget={observation.remaining_compute_budget}
        remaining_latency_budget_ms={observation.remaining_latency_budget_ms}
        visible_alerts:
        {alerts}
        """
    ).strip()


def llm_action(client: OpenAI, observation) -> SocAction:
    if API_KEY == "demo-key":
        return heuristic_action(observation)
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt_for_model(observation)},
            ],
            temperature=0.1,
            max_tokens=80,
            stream=False,
        )
        text = (response.choices[0].message.content or "").strip()
        parts = [part.strip() for part in text.split("|")]
        if len(parts) != 5:
            return heuristic_action(observation)
        action_name, target_alert_id, tool_name, model_tier, escalate = parts
        return SocAction(
            response_action=ResponseAction(action_name),
            target_alert_id=None if target_alert_id == "none" else target_alert_id,
            tool_name=ToolName(tool_name),
            model_tier=ModelTier(model_tier),
            escalate_severity=None if escalate == "none" else Severity(escalate),
            reasoning_note="llm_policy",
        )
    except Exception:
        return heuristic_action(observation)


async def main() -> None:
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    env = SocGuardianEnv(task_name=TASK_NAME)

    rewards: List[float] = []
    steps_taken = 0
    success = False
    score = 0.0

    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)
    result = await env.reset()
    try:
        for step in range(1, MAX_STEPS + 1):
            if result.done:
                break
            action = llm_action(client, result.observation)
            action_text = f"{action.response_action.value}({action.target_alert_id or 'none'})/{action.tool_name.value}/{action.model_tier.value}"
            result = await env.step(action)
            rewards.append(result.reward)
            steps_taken = step
            log_step(step, action_text, result.reward, result.done, result.info.last_action_error)
            if result.done:
                break
        state = await env.state()
        score = min(max(state.final_score, 0.0), 1.0)
        success = score >= SUCCESS_SCORE_THRESHOLD and state.breach_occurred is False
    finally:
        try:
            await env.close()
        except Exception:
            pass
        log_end(success, steps_taken, score, rewards)


if __name__ == "__main__":
    asyncio.run(main())
