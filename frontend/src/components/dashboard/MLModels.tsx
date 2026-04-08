import { useState, useEffect } from 'react';
import { DashboardCard } from './DashboardCard';
import type { AttackPhase, AnomalyLevel, LLMTier } from '@/lib/simulation';

const phaseLabels: Record<AttackPhase, string> = {
  social_engineering: 'Social Engineering',
  initial_access: 'Initial Access',
  privilege_escalation: 'Privilege Escalation',
  lateral_movement: 'Lateral Movement',
};

const phaseColors: Record<AttackPhase, string> = {
  social_engineering: 'text-info',
  initial_access: 'text-warning',
  privilege_escalation: 'text-destructive',
  lateral_movement: 'text-destructive',
};

const anomalyColors: Record<AnomalyLevel, string> = {
  normal: 'text-success',
  suspicious: 'text-warning',
  critical: 'text-destructive',
};

const tierInfo: Record<LLMTier, { label: string; cost: string; color: string }> = {
  fast: { label: 'Fast LLM (Cheap)', cost: '$0.01', color: 'text-success' },
  mid: { label: 'Mid-Tier LLM', cost: '$0.05', color: 'text-warning' },
  premium: { label: 'Premium LLM (Deep)', cost: '$0.20', color: 'text-destructive' },
};

export function MLModels() {
  const [phase, setPhase] = useState<AttackPhase>('social_engineering');
  const [anomaly, setAnomaly] = useState({ score: 0.23, level: 'normal' as AnomalyLevel });
  const [tier, setTier] = useState<LLMTier>('fast');
  const [budget, setBudget] = useState(1.0);

  useEffect(() => {
    const phases: AttackPhase[] = ['social_engineering', 'initial_access', 'privilege_escalation', 'lateral_movement'];
    let idx = 0;
    const interval = setInterval(() => {
      idx = (idx + 1) % phases.length;
      setPhase(phases[idx]);
      const score = +(Math.random()).toFixed(3);
      const level: AnomalyLevel = score < 0.35 ? 'normal' : score < 0.7 ? 'suspicious' : 'critical';
      setAnomaly({ score, level });
      setTier(score > 0.7 ? 'premium' : score > 0.4 ? 'mid' : 'fast');
      setBudget(b => Math.max(0, +(b - [0.01, 0.05, 0.2][score > 0.7 ? 2 : score > 0.4 ? 1 : 0]).toFixed(2)));
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <DashboardCard title="ML1 — Phase Classifier" subtitle="CNN/LSTM" variant="purple">
        <div className="space-y-2">
          {(Object.keys(phaseLabels) as AttackPhase[]).map(p => (
            <div key={p} className={`flex items-center justify-between text-xs font-mono px-2 py-1 rounded transition-all ${p === phase ? 'bg-accent/20' : ''}`}>
              <span className={p === phase ? phaseColors[p] : 'text-muted-foreground'}>{phaseLabels[p]}</span>
              {p === phase && <span className={`font-bold ${phaseColors[p]}`}>◄ ACTIVE</span>}
            </div>
          ))}
        </div>
      </DashboardCard>

      <DashboardCard title="ML2 — Anomaly Detector" subtitle="Isolation Forest">
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground font-mono">Score</span>
            <span className={`text-lg font-bold font-mono ${anomalyColors[anomaly.level]}`}>{anomaly.score}</span>
          </div>
          <div className="h-2 rounded-full bg-secondary overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${anomaly.level === 'normal' ? 'bg-success' : anomaly.level === 'suspicious' ? 'bg-warning' : 'bg-destructive'}`}
              style={{ width: `${anomaly.score * 100}%` }}
            />
          </div>
          <div className={`text-center text-xs font-bold uppercase ${anomalyColors[anomaly.level]}`}>{anomaly.level}</div>
        </div>
      </DashboardCard>

      <DashboardCard title="ML3 — LLM Router" subtitle={`Budget: $${budget.toFixed(2)}`}>
        <div className="space-y-2">
          {(Object.entries(tierInfo) as [LLMTier, typeof tierInfo['fast']][]).map(([t, info]) => (
            <div key={t} className={`flex items-center justify-between text-xs font-mono px-2 py-1.5 rounded transition-all ${t === tier ? 'bg-secondary' : ''}`}>
              <span className={t === tier ? info.color : 'text-muted-foreground'}>{info.label}</span>
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground">{info.cost}</span>
                {t === tier && <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${info.color} bg-secondary`}>SELECTED</span>}
              </div>
            </div>
          ))}
        </div>
      </DashboardCard>
    </div>
  );
}
