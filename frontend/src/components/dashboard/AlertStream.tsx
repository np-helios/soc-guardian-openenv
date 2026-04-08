import { useEffect, useState } from 'react';
import { DashboardCard } from './DashboardCard';
import { generateAlert, type Alert } from '@/lib/simulation';

const sevColors: Record<string, string> = {
  low: 'text-success',
  medium: 'text-info',
  high: 'text-warning',
  critical: 'text-destructive',
};

const srcBadge: Record<string, string> = {
  SIEM: 'bg-primary/20 text-primary',
  EDR: 'bg-accent/20 text-accent',
  IAM: 'bg-warning/20 text-warning',
};

export function AlertStream() {
  const [alerts, setAlerts] = useState<Alert[]>(() =>
    Array.from({ length: 8 }, (_, i) => generateAlert(i))
  );

  useEffect(() => {
    let idx = 8;
    const interval = setInterval(() => {
      setAlerts(prev => [generateAlert(idx++), ...prev.slice(0, 11)]);
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  return (
    <DashboardCard title="Layer 0 — Alert Ingestion Stream" subtitle="LIVE" variant="cyan">
      <div className="space-y-1.5 max-h-64 overflow-y-auto scrollbar-thin">
        {alerts.map((a) => (
          <div
            key={a.id}
            className="flex items-center gap-3 rounded bg-secondary/50 px-3 py-1.5 font-mono text-xs transition-all hover:bg-secondary"
          >
            <span className="text-muted-foreground w-16 shrink-0">{a.id}</span>
            <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${srcBadge[a.source]}`}>{a.source}</span>
            <span className={`font-bold uppercase w-14 ${sevColors[a.severity]}`}>{a.severity}</span>
            <span className="text-foreground/70 truncate flex-1">{a.description}</span>
            <span className="text-muted-foreground text-[10px] shrink-0">
              {new Date(a.timestamp).toLocaleTimeString()}
            </span>
          </div>
        ))}
      </div>
      <div className="mt-2 h-1 w-full rounded bg-secondary overflow-hidden">
        <div className="h-full w-1/3 bg-primary/60 animate-data-flow rounded" />
      </div>
    </DashboardCard>
  );
}
