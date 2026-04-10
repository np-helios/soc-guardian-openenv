export type Severity = "low" | "medium" | "high" | "critical";
export type ResponseAction =
  | "ignore"
  | "investigate"
  | "request_verification"
  | "escalate_to_human"
  | "flag_anomaly"
  | "block_user"
  | "isolate_host"
  | "trigger_incident_response"
  | "open_incident";
export type ToolName = "none" | "log_analyzer" | "identity_verifier" | "network_monitor";
export type ModelTier = "cheap" | "balanced" | "deep";

export interface VisibleAlert {
  alert_id: string;
  title: string;
  severity: Severity;
  signal_strength: number;
  source: string;
  description: string;
  tags: string[];
  observed_at: string;
}

export interface ToolProfile {
  name: ToolName;
  cost_units: number;
  latency_ms: number;
  accuracy: number;
  summary: string;
}

export interface ModelProfile {
  tier: ModelTier;
  cost_units: number;
  latency_ms: number;
  reasoning_quality: number;
}

export interface SocObservation {
  benchmark: string;
  task_name: string;
  step_index: number;
  max_steps: number;
  visible_alerts: VisibleAlert[];
  system_risk_level: number;
  attacker_progression_score: number;
  remaining_compute_budget: number;
  remaining_latency_budget_ms: number;
  incident_open: boolean;
  incident_severity: Severity | null;
  previous_actions: string[];
  available_tools: ToolProfile[];
  available_models: ModelProfile[];
  analyst_notes: string[];
}

export interface SocStepInfo {
  tool_used: ToolName;
  model_used: ModelTier;
  cost_incurred: number;
  latency_incurred_ms: number;
  detection_gain: number;
  false_positive_penalty: number;
  false_negative_penalty: number;
  early_detection_bonus: number;
  breach_prevented: boolean;
  incident_opened_correctly: boolean;
  grader_score: number;
  last_action_error: string | null;
}

export interface SocStepResult {
  observation: SocObservation;
  reward: number;
  done: boolean;
  info: SocStepInfo;
}

export interface SocState {
  benchmark: string;
  task_name: string;
  seed: number;
  step_index: number;
  max_steps: number;
  system_risk_level: number;
  attacker_progression_score: number;
  remaining_compute_budget: number;
  remaining_latency_budget_ms: number;
  incident_open: boolean;
  incident_severity: Severity | null;
  cumulative_reward: number;
  cumulative_cost: number;
  cumulative_latency_ms: number;
  false_positive_count: number;
  false_negative_count: number;
  processed_alert_ids: string[];
  remaining_alert_ids: string[];
  breach_prevented: boolean;
  breach_occurred: boolean;
  final_score: number;
}

export interface SocActionPayload {
  response_action: ResponseAction;
  target_alert_id: string | null;
  tool_name: ToolName;
  model_tier: ModelTier;
  escalate_severity: Severity | null;
  reasoning_note: string | null;
}

export interface DemoDecision {
  action: SocActionPayload;
  rationale: string[];
}

export interface DemoSocResponse {
  summary: string;
  suggested_task: string;
  decision: DemoDecision;
  estimated_cost_units: number;
  estimated_latency_ms: number;
}

export interface TaskDescriptor {
  id: string;
  name?: string;
  description?: string;
  difficulty?: string;
  has_grader?: boolean;
  grader?: {
    type?: string;
    enabled?: boolean;
    score_range?: [number, number];
  };
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";

async function jsonFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const text = await response.text();
  const data = text ? JSON.parse(text) : null;
  if (!response.ok) {
    throw new Error(data?.detail || text || `Request failed with ${response.status}`);
  }
  return data as T;
}

export async function healthCheck(): Promise<{ status: string }> {
  return jsonFetch<{ status: string }>("/health");
}

export async function listTasks(): Promise<{
  tasks: Array<string | TaskDescriptor>;
  task_names?: string[];
  tasks_with_graders?: number;
}> {
  return jsonFetch<{
    tasks: Array<string | TaskDescriptor>;
    task_names?: string[];
    tasks_with_graders?: number;
  }>("/tasks");
}

export async function resetScenario(taskName: string, seed: number): Promise<SocStepResult> {
  return jsonFetch<SocStepResult>("/reset", {
    method: "POST",
    body: JSON.stringify({ task_name: taskName, seed }),
  });
}

export async function sendStep(action: SocActionPayload): Promise<SocStepResult> {
  return jsonFetch<SocStepResult>("/step", {
    method: "POST",
    body: JSON.stringify(action),
  });
}

export async function fetchState(): Promise<SocState> {
  return jsonFetch<SocState>("/state");
}

export async function closeScenario(): Promise<{ status: string }> {
  return jsonFetch<{ status: string }>("/close", { method: "POST" });
}

export async function demoQuery(query: string): Promise<DemoSocResponse> {
  return jsonFetch<DemoSocResponse>("/demo/query", {
    method: "POST",
    body: JSON.stringify({ query }),
  });
}
