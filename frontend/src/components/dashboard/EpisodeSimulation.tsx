import { useState, useMemo } from 'react';
import { DashboardCard } from './DashboardCard';
import { TASKS, generateEpisodeSteps, computeMetrics, type TaskConfig, type EpisodeStep } from '@/lib/simulation';
import { Play, RotateCcw } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

export function EpisodeSimulation() {
  const [selectedTask, setSelectedTask] = useState<TaskConfig>(TASKS[1]);
  const [steps, setSteps] = useState<EpisodeStep[]>(() => generateEpisodeSteps(TASKS[1]));

  const metrics = useMemo(() => computeMetrics(steps), [steps]);

  const runEpisode = () => {
    setSteps(generateEpisodeSteps(selectedTask));
  };

  const difficultyColor = {
    easy: 'text-success',
    medium: 'text-warning',
    hard: 'text-destructive',
  };

  return (
    <div className="space-y-4">
      <DashboardCard title="OpenEnv Tasks & Episode Simulation" subtitle="MGM Replay" variant="purple">
        <div className="flex flex-wrap gap-2 mb-4">
          {TASKS.map(t => (
            <button
              key={t.id}
              onClick={() => { setSelectedTask(t); setSteps(generateEpisodeSteps(t)); }}
              className={`px-3 py-1.5 rounded text-xs font-mono transition-all ${
                t.id === selectedTask.id
                  ? 'bg-accent text-accent-foreground'
                  : 'bg-secondary text-muted-foreground hover:text-foreground'
              }`}
            >
              <span className={difficultyColor[t.difficulty]}>{t.difficulty.toUpperCase()}</span>
              <span className="ml-2">{t.name}</span>
            </button>
          ))}
        </div>

        <div className="rounded bg-secondary/50 p-3 mb-4">
          <p className="text-xs text-muted-foreground font-mono">{selectedTask.description}</p>
          <div className="flex gap-4 mt-2 text-[10px] font-mono text-muted-foreground">
            <span>Speed: {selectedTask.attackSpeed}</span>
            <span>Stealth: {selectedTask.stealthLevel}</span>
            <span>Adaptive: {selectedTask.adaptiveAttacker ? 'YES' : 'NO'}</span>
            <span>Max Steps: {selectedTask.maxSteps}</span>
          </div>
        </div>

        <div className="flex gap-2 mb-4">
          <button onClick={runEpisode} className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-primary text-primary-foreground text-xs font-mono font-bold hover:opacity-90 transition">
            <Play className="h-3 w-3" /> Run Episode
          </button>
          <button onClick={runEpisode} className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-secondary text-foreground text-xs font-mono hover:bg-secondary/80 transition">
            <RotateCcw className="h-3 w-3" /> Reset
          </button>
        </div>

        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={steps}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(220 15% 18%)" />
              <XAxis dataKey="step" tick={{ fontSize: 10, fill: 'hsl(215 15% 50%)' }} />
              <YAxis tick={{ fontSize: 10, fill: 'hsl(215 15% 50%)' }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(220 18% 10%)',
                  border: '1px solid hsl(220 15% 18%)',
                  borderRadius: '6px',
                  fontSize: '11px',
                  fontFamily: 'JetBrains Mono',
                }}
              />
              <Line type="monotone" dataKey="cumulativeReward" stroke="hsl(180 100% 50%)" strokeWidth={2} dot={false} name="Cum. Reward" />
              <Line type="monotone" dataKey="anomalyScore" stroke="hsl(280 80% 60%)" strokeWidth={1.5} dot={false} name="Anomaly" />
              <Line type="monotone" dataKey="computeCost" stroke="hsl(40 95% 55%)" strokeWidth={1} dot={false} name="Cost" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </DashboardCard>

      <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
        {[
          { label: 'Detection Rate', value: `${(metrics.detectionRate * 100).toFixed(1)}%`, color: 'text-success' },
          { label: 'Response Time', value: `${metrics.responseTime} steps`, color: 'text-primary' },
          { label: 'Cost/Alert', value: `$${metrics.costEfficiency}`, color: 'text-warning' },
          { label: 'FP Rate', value: `${(metrics.falsePositiveRate * 100).toFixed(1)}%`, color: 'text-info' },
          { label: 'FN Rate', value: `${(metrics.falseNegativeRate * 100).toFixed(1)}%`, color: 'text-destructive' },
          { label: 'Total Reward', value: `${metrics.totalReward}`, color: metrics.totalReward >= 0 ? 'text-success' : 'text-destructive' },
        ].map(m => (
          <div key={m.label} className="bg-card rounded-lg border border-border p-3 text-center">
            <div className="text-[10px] text-muted-foreground font-mono uppercase">{m.label}</div>
            <div className={`text-lg font-bold font-mono ${m.color}`}>{m.value}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
