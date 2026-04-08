import { DashboardCard } from './DashboardCard';
import { CheckCircle2 } from 'lucide-react';

export function OpenEnvSpec() {
  const specItems = [
    { label: 'Typed Models', desc: 'SocObservation, SocAction, SocState, SocStepResult' },
    { label: 'step() / reset() / state()', desc: 'Full OpenEnv-style lifecycle implemented' },
    { label: 'openenv.yaml', desc: 'Environment config with task metadata and entrypoint' },
    { label: '3 Tasks (Easy→Hard)', desc: 'Helpdesk takeover, privilege spiral, lateral breach' },
    { label: 'Agent Graders', desc: 'Hidden targets scored 0.0–1.0 with partial progress' },
    { label: 'Reward Function', desc: 'Detection, early response, false positives, cost, latency' },
    { label: 'Baseline Script', desc: 'Reproducible inference.py with standard stdout format' },
    { label: 'Dockerfile', desc: 'HF Space / container deployment ready' },
    { label: 'README', desc: 'Action space, observation space, setup, architecture' },
  ];

  return (
    <DashboardCard title="OpenEnv Spec Compliance" variant="cyan">
      <div className="space-y-1.5">
        {specItems.map(item => (
          <div key={item.label} className="flex items-start gap-2">
            <CheckCircle2 className="h-3.5 w-3.5 text-success mt-0.5 shrink-0" />
            <div>
              <span className="text-xs font-mono font-bold text-foreground">{item.label}</span>
              <span className="text-xs text-muted-foreground ml-2">{item.desc}</span>
            </div>
          </div>
        ))}
      </div>
    </DashboardCard>
  );
}
