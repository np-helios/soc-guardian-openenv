import { useState, useEffect } from 'react';
import { DashboardCard } from './DashboardCard';
import type { AgentAction, DiagnosticTool, LLMTier } from '@/lib/simulation';

const actionLabels: Record<AgentAction, { label: string; color: string }> = {
  ignore: { label: 'IGNORE', color: 'text-muted-foreground' },
  investigate: { label: 'INVESTIGATE', color: 'text-info' },
  escalate: { label: 'ESCALATE', color: 'text-warning' },
  block: { label: 'BLOCK', color: 'text-destructive' },
  isolate: { label: 'ISOLATE', color: 'text-destructive' },
};

const toolLabels: Record<DiagnosticTool, string> = {
  log_analyzer: 'Log Analyzer',
  identity_verifier: 'Identity Verifier',
  network_monitor: 'Network Monitor',
};

export function PPOAgent() {
  const [action, setAction] = useState<AgentAction>('investigate');
  const [tool, setTool] = useState<DiagnosticTool>('log_analyzer');
  const [llm, setLlm] = useState<LLMTier>('fast');
  const [reward, setReward] = useState(0);
  const [cumReward, setCumReward] = useState(0);

  useEffect(() => {
    const actions: AgentAction[] = ['ignore', 'investigate', 'escalate', 'block', 'isolate'];
    const tools: DiagnosticTool[] = ['log_analyzer', 'identity_verifier', 'network_monitor'];
    const tiers: LLMTier[] = ['fast', 'mid', 'premium'];

    const interval = setInterval(() => {
      const a = actions[Math.floor(Math.random() * actions.length)];
      setAction(a);
      setTool(tools[Math.floor(Math.random() * tools.length)]);
      setLlm(tiers[Math.floor(Math.random() * tiers.length)]);
      const r = +((Math.random() - 0.3) * 2).toFixed(3);
      setReward(r);
      setCumReward(c => +(c + r).toFixed(3));
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <DashboardCard title="PPO Agent — Decision Engine" subtitle="3-Head Policy" variant="cyan">
      <div className="grid grid-cols-3 gap-4">
        <div>
          <div className="text-[10px] text-muted-foreground font-mono uppercase mb-1">Security Action</div>
          <div className="space-y-1">
            {(Object.entries(actionLabels) as [AgentAction, typeof actionLabels['ignore']][]).map(([a, info]) => (
              <div key={a} className={`text-xs font-mono px-2 py-0.5 rounded transition-all ${a === action ? `${info.color} bg-secondary font-bold` : 'text-muted-foreground/40'}`}>
                {info.label}
              </div>
            ))}
          </div>
        </div>
        <div>
          <div className="text-[10px] text-muted-foreground font-mono uppercase mb-1">Diagnostic Tool</div>
          <div className="space-y-1">
            {(Object.entries(toolLabels) as [DiagnosticTool, string][]).map(([t, label]) => (
              <div key={t} className={`text-xs font-mono px-2 py-0.5 rounded transition-all ${t === tool ? 'text-primary bg-secondary font-bold' : 'text-muted-foreground/40'}`}>
                {label}
              </div>
            ))}
          </div>
        </div>
        <div>
          <div className="text-[10px] text-muted-foreground font-mono uppercase mb-1">Reward Signal</div>
          <div className="space-y-2 mt-1">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-muted-foreground">Step</span>
              <span className={reward >= 0 ? 'text-success' : 'text-destructive'}>{reward >= 0 ? '+' : ''}{reward}</span>
            </div>
            <div className="flex justify-between text-xs font-mono">
              <span className="text-muted-foreground">Cumulative</span>
              <span className={cumReward >= 0 ? 'text-success' : 'text-destructive'}>{cumReward >= 0 ? '+' : ''}{cumReward}</span>
            </div>
            <div className="text-[10px] text-muted-foreground font-mono">LLM: {llm.toUpperCase()}</div>
          </div>
        </div>
      </div>
    </DashboardCard>
  );
}
