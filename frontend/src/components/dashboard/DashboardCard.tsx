import { ReactNode } from 'react';

interface DashboardCardProps {
  title: string;
  subtitle?: string;
  children: ReactNode;
  variant?: 'default' | 'cyan' | 'purple' | 'danger';
  className?: string;
}

const glowClasses = {
  default: 'border-border',
  cyan: 'border-primary/30 border-glow-cyan',
  purple: 'border-accent/30 border-glow-purple',
  danger: 'border-destructive/30',
};

export function DashboardCard({ title, subtitle, children, variant = 'default', className = '' }: DashboardCardProps) {
  return (
    <div className={`bg-card rounded-lg border ${glowClasses[variant]} p-4 ${className}`}>
      <div className="mb-3 flex items-baseline justify-between">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-foreground">{title}</h3>
        {subtitle && <span className="text-xs font-mono text-muted-foreground">{subtitle}</span>}
      </div>
      {children}
    </div>
  );
}
