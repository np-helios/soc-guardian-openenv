import { DashboardCard } from './DashboardCard';

export function RewardFunction() {
  const terms = [
    { symbol: '+', label: 'breach_prevented', weight: '+10.0', color: 'text-success' },
    { symbol: '+', label: 'early_detection_bonus', weight: '+5.0 × (1 − t/T)', color: 'text-success' },
    { symbol: '−', label: 'false_negative_penalty', weight: '−8.0', color: 'text-destructive' },
    { symbol: '−', label: 'false_positive_penalty', weight: '−2.0', color: 'text-warning' },
    { symbol: '−', label: 'compute_cost', weight: '−tier_cost', color: 'text-warning' },
    { symbol: '−', label: 'latency', weight: '−0.01/step', color: 'text-muted-foreground' },
  ];

  return (
    <DashboardCard title="Reward Function" subtitle="Asymmetric Design">
      <div className="bg-secondary/50 rounded p-3 font-mono text-xs space-y-1">
        <div className="text-muted-foreground mb-2">R = Σ</div>
        {terms.map(t => (
          <div key={t.label} className="flex items-center gap-2">
            <span className={t.color}>{t.symbol}</span>
            <span className="text-foreground/80 flex-1">{t.label}</span>
            <span className={`${t.color} font-bold`}>{t.weight}</span>
          </div>
        ))}
      </div>
      <div className="mt-2 text-[10px] text-muted-foreground font-mono">
        * Missing an attack (FN) penalized 4× more than false alarm (FP)
      </div>
    </DashboardCard>
  );
}
