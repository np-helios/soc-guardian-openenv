import { DashboardCard } from './DashboardCard';

interface LayerNode {
  label: string;
  sub: string;
  color: string;
}

export function ArchitectureDiagram() {
  const layers: LayerNode[] = [
    { label: 'L0', sub: 'Alert Ingestion', color: 'border-primary/50 text-primary' },
    { label: 'L1', sub: 'Identity Gate', color: 'border-success/50 text-success' },
    { label: 'L2', sub: 'SOC State', color: 'border-info/50 text-info' },
    { label: 'T1', sub: 'Tool Selector', color: 'border-warning/50 text-warning' },
    { label: 'M1', sub: 'Model Router', color: 'border-accent/50 text-accent' },
    { label: 'D1', sub: 'Response Engine', color: 'border-primary/50 text-primary' },
    { label: 'ENV', sub: 'Attack Simulator', color: 'border-destructive/50 text-destructive' },
    { label: 'GRD', sub: 'Reward & Grader', color: 'border-success/50 text-success' },
  ];

  return (
    <DashboardCard title="System Architecture" subtitle="Live SOC Pipeline">
      <div className="flex items-center gap-1 overflow-x-auto py-2">
        {layers.map((l, i) => (
          <div key={l.label} className="flex items-center shrink-0">
            <div className={`border rounded px-2.5 py-2 text-center ${l.color}`}>
              <div className="text-xs font-bold font-mono">{l.label}</div>
              <div className="text-[9px] text-muted-foreground whitespace-nowrap">{l.sub}</div>
            </div>
            {i < layers.length - 1 && (
              <span className="text-muted-foreground/40 text-xs mx-0.5">→</span>
            )}
          </div>
        ))}
      </div>
    </DashboardCard>
  );
}
