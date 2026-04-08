interface StatusIndicatorProps {
  status: 'online' | 'warning' | 'critical' | 'offline';
  label: string;
  size?: 'sm' | 'md';
}

const colors = {
  online: 'bg-success',
  warning: 'bg-warning',
  critical: 'bg-destructive',
  offline: 'bg-muted-foreground',
};

export function StatusIndicator({ status, label, size = 'sm' }: StatusIndicatorProps) {
  const dotSize = size === 'sm' ? 'h-2 w-2' : 'h-3 w-3';
  return (
    <div className="flex items-center gap-2">
      <span className={`${dotSize} rounded-full ${colors[status]} animate-pulse-glow`} />
      <span className="text-xs text-muted-foreground font-mono uppercase tracking-wider">{label}</span>
    </div>
  );
}
