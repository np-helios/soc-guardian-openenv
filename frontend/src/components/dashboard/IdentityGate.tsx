import { useState, useEffect } from 'react';
import { DashboardCard } from './DashboardCard';
import { Shield, Fingerprint, Smartphone, KeyRound, CheckCircle2, XCircle, Loader2 } from 'lucide-react';

type StepStatus = 'pending' | 'verifying' | 'passed' | 'failed';

interface GateStep {
  id: string;
  label: string;
  icon: React.ReactNode;
  status: StepStatus;
}

export function IdentityGate() {
  const [steps, setSteps] = useState<GateStep[]>([
    { id: 'biometric', label: 'Biometric Scan (Fingerprint/Face/Iris)', icon: <Fingerprint className="h-4 w-4" />, status: 'pending' },
    { id: 'aadhaar', label: 'Aadhaar OTP via UIDAI API', icon: <Smartphone className="h-4 w-4" />, status: 'pending' },
    { id: '2fa', label: 'Admin 2FA (TOTP) + Role Validation', icon: <KeyRound className="h-4 w-4" />, status: 'pending' },
  ]);
  const [cycle, setCycle] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => setCycle(c => c + 1), 6000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    setSteps(s => s.map(step => ({ ...step, status: 'pending' as StepStatus })));

    const timers = [
      setTimeout(() => setSteps(s => s.map((step, i) => i === 0 ? { ...step, status: 'verifying' } : step)), 500),
      setTimeout(() => setSteps(s => s.map((step, i) => i === 0 ? { ...step, status: 'passed' } : i === 1 ? { ...step, status: 'verifying' } : step)), 1800),
      setTimeout(() => setSteps(s => s.map((step, i) => i === 1 ? { ...step, status: Math.random() > 0.15 ? 'passed' : 'failed' } : i === 2 ? { ...step, status: 'verifying' } : step)), 3200),
      setTimeout(() => setSteps(s => {
        const prevFailed = s.some(st => st.status === 'failed');
        return s.map((step, i) => i === 2 ? { ...step, status: prevFailed ? 'pending' : (Math.random() > 0.1 ? 'passed' : 'failed') } : step);
      }), 4800),
    ];

    return () => timers.forEach(clearTimeout);
  }, [cycle]);

  const allPassed = steps.every(s => s.status === 'passed');
  const anyFailed = steps.some(s => s.status === 'failed');

  const statusIcon = (s: StepStatus) => {
    switch (s) {
      case 'pending': return <span className="h-4 w-4 rounded-full border border-muted-foreground/30" />;
      case 'verifying': return <Loader2 className="h-4 w-4 text-primary animate-spin" />;
      case 'passed': return <CheckCircle2 className="h-4 w-4 text-success" />;
      case 'failed': return <XCircle className="h-4 w-4 text-destructive" />;
    }
  };

  return (
    <DashboardCard
      title="Layer 1 — Identity Verification Gate"
      subtitle={allPassed ? '✓ AUTHORIZED' : anyFailed ? '✗ DENIED' : 'VERIFYING…'}
      variant={allPassed ? 'cyan' : anyFailed ? 'danger' : 'default'}
    >
      <div className="space-y-3">
        {steps.map((step) => (
          <div key={step.id} className="flex items-center gap-3">
            <div className="text-muted-foreground">{step.icon}</div>
            <span className="text-xs font-mono flex-1 text-foreground/80">{step.label}</span>
            {statusIcon(step.status)}
          </div>
        ))}
      </div>
      {anyFailed && (
        <div className="mt-3 rounded bg-destructive/10 border border-destructive/20 px-3 py-2 text-xs font-mono text-destructive">
          ⚠ Tamper log appended — action denied. Insider threat flag raised.
        </div>
      )}
      {allPassed && (
        <div className="mt-3 rounded bg-success/10 border border-success/20 px-3 py-2 text-xs font-mono text-success flex items-center gap-2">
          <Shield className="h-3 w-3" /> Identity verified — action authorized
        </div>
      )}
    </DashboardCard>
  );
}
