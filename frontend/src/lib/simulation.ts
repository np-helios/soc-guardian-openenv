// Simulated data generators for the cybersecurity RL dashboard

export type AlertSeverity = 'low' | 'medium' | 'high' | 'critical';
export type AttackPhase = 'social_engineering' | 'initial_access' | 'privilege_escalation' | 'lateral_movement';
export type AnomalyLevel = 'normal' | 'suspicious' | 'critical';
export type AgentAction = 'ignore' | 'investigate' | 'escalate' | 'block' | 'isolate';
export type DiagnosticTool = 'log_analyzer' | 'identity_verifier' | 'network_monitor';
export type LLMTier = 'fast' | 'mid' | 'premium';
export type VerificationStep = 'biometric' | 'aadhaar_otp' | 'admin_2fa';

export interface Alert {
  id: string;
  timestamp: string;
  source: 'SIEM' | 'EDR' | 'IAM';
  severity: AlertSeverity;
  signal: number[];
  description: string;
}

export interface StateVector {
  alertSignals: number[];
  severityScores: number[];
  actionHistory: AgentAction[];
  riskLevel: number;
  computeBudget: number;
}

export interface EpisodeStep {
  step: number;
  phase: AttackPhase;
  anomalyScore: number;
  anomalyLevel: AnomalyLevel;
  agentAction: AgentAction;
  tool: DiagnosticTool;
  llmTier: LLMTier;
  reward: number;
  cumulativeReward: number;
  computeCost: number;
  detected: boolean;
}

export interface TaskConfig {
  id: string;
  name: string;
  difficulty: 'easy' | 'medium' | 'hard';
  description: string;
  attackSpeed: number;
  stealthLevel: number;
  adaptiveAttacker: boolean;
  maxSteps: number;
}

export interface EvalMetrics {
  detectionRate: number;
  costEfficiency: number;
  responseTime: number;
  falsePositiveRate: number;
  falseNegativeRate: number;
  totalReward: number;
}

export const TASKS: TaskConfig[] = [
  {
    id: 'task_easy',
    name: 'Basic Phishing Detection',
    difficulty: 'easy',
    description: 'Single-vector phishing attack with clear signatures. Low stealth, fixed pattern.',
    attackSpeed: 0.3,
    stealthLevel: 0.2,
    adaptiveAttacker: false,
    maxSteps: 20,
  },
  {
    id: 'task_medium',
    name: 'MGM-Style Social Engineering',
    difficulty: 'medium',
    description: 'Multi-stage social engineering to helpdesk, then privilege escalation via Okta. Moderate stealth.',
    attackSpeed: 0.6,
    stealthLevel: 0.5,
    adaptiveAttacker: false,
    maxSteps: 40,
  },
  {
    id: 'task_hard',
    name: 'Adaptive APT Campaign',
    difficulty: 'hard',
    description: 'Adaptive attacker agent that changes tactics based on defender actions. High stealth, multi-vector.',
    attackSpeed: 0.8,
    stealthLevel: 0.8,
    adaptiveAttacker: true,
    maxSteps: 60,
  },
];

const ALERT_DESCRIPTIONS = [
  'Unusual login from unrecognized device',
  'Elevated API call rate from service account',
  'Permission change on admin group',
  'Lateral movement pattern detected',
  'Failed MFA attempt from known IP',
  'New SSH key added to production server',
  'Data exfiltration pattern in egress traffic',
  'Helpdesk ticket: password reset for VIP account',
  'Registry modification on endpoint',
  'Anomalous DNS query volume',
];

export function generateAlert(index: number): Alert {
  const sources: Alert['source'][] = ['SIEM', 'EDR', 'IAM'];
  const severities: AlertSeverity[] = ['low', 'medium', 'high', 'critical'];
  const now = new Date();
  now.setSeconds(now.getSeconds() - Math.random() * 60);

  return {
    id: `ALT-${String(index).padStart(4, '0')}`,
    timestamp: now.toISOString(),
    source: sources[Math.floor(Math.random() * sources.length)],
    severity: severities[Math.floor(Math.random() * severities.length)],
    signal: Array.from({ length: 8 }, () => +(Math.random()).toFixed(3)),
    description: ALERT_DESCRIPTIONS[Math.floor(Math.random() * ALERT_DESCRIPTIONS.length)],
  };
}

export function generateEpisodeSteps(task: TaskConfig): EpisodeStep[] {
  const phases: AttackPhase[] = ['social_engineering', 'initial_access', 'privilege_escalation', 'lateral_movement'];
  const actions: AgentAction[] = ['ignore', 'investigate', 'escalate', 'block', 'isolate'];
  const tools: DiagnosticTool[] = ['log_analyzer', 'identity_verifier', 'network_monitor'];
  const tiers: LLMTier[] = ['fast', 'mid', 'premium'];

  const steps: EpisodeStep[] = [];
  let cumReward = 0;
  let phaseIdx = 0;

  for (let i = 0; i < task.maxSteps; i++) {
    if (i > 0 && i % Math.ceil(task.maxSteps / 4) === 0 && phaseIdx < 3) phaseIdx++;

    const anomalyScore = Math.min(1, (task.stealthLevel * 0.3 + Math.random() * 0.7) * (1 + phaseIdx * 0.2));
    const anomalyLevel: AnomalyLevel = anomalyScore < 0.35 ? 'normal' : anomalyScore < 0.7 ? 'suspicious' : 'critical';

    const actionIdx = anomalyScore > 0.7 ? Math.min(4, 3 + Math.floor(Math.random() * 2)) : Math.floor(Math.random() * 3);
    const tierIdx = anomalyScore > 0.7 ? 2 : anomalyScore > 0.4 ? 1 : 0;

    const computeCost = [0.01, 0.05, 0.2][tierIdx];
    const detected = actionIdx >= 3 && anomalyScore > 0.5;
    const reward = detected ? 1.0 + (1 - i / task.maxSteps) * 0.5 : anomalyScore > 0.6 && actionIdx < 2 ? -0.8 : -computeCost;
    cumReward += reward;

    steps.push({
      step: i,
      phase: phases[phaseIdx],
      anomalyScore: +anomalyScore.toFixed(3),
      anomalyLevel,
      agentAction: actions[actionIdx],
      tool: tools[Math.floor(Math.random() * tools.length)],
      llmTier: tiers[tierIdx],
      reward: +reward.toFixed(3),
      cumulativeReward: +cumReward.toFixed(3),
      computeCost: +computeCost.toFixed(3),
      detected,
    });

    if (detected && Math.random() > 0.5) break;
  }

  return steps;
}

export function computeMetrics(steps: EpisodeStep[]): EvalMetrics {
  const truePositives = steps.filter(s => s.detected).length;
  const falseNegatives = steps.filter(s => s.anomalyLevel === 'critical' && !s.detected).length;
  const falsePositives = steps.filter(s => s.anomalyLevel === 'normal' && (s.agentAction === 'block' || s.agentAction === 'isolate')).length;
  const totalCost = steps.reduce((s, e) => s + e.computeCost, 0);
  const firstDetection = steps.findIndex(s => s.detected);

  return {
    detectionRate: +(truePositives / Math.max(1, truePositives + falseNegatives)).toFixed(3),
    costEfficiency: +(totalCost / steps.length).toFixed(4),
    responseTime: firstDetection >= 0 ? firstDetection : steps.length,
    falsePositiveRate: +(falsePositives / steps.length).toFixed(3),
    falseNegativeRate: +(falseNegatives / Math.max(1, steps.length)).toFixed(3),
    totalReward: +steps[steps.length - 1].cumulativeReward.toFixed(3),
  };
}
