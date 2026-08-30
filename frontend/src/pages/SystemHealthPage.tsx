import React, { useState, useEffect } from 'react';
import { HeartPulse, CheckCircle2, RotateCcw, Cpu } from 'lucide-react';
import { api } from '../services/api';
import { SystemHealthMetric } from '../types';
import { GlassCard, GlassDeep } from '../components/common/GlassWrappers';
import { StatusBadge } from '../components/common/StatusBadge';
import { useCase } from '../context/CaseContext';
import { useDocumentTitle } from '../hooks/useDocumentTitle';

export const SystemHealthPage: React.FC = () => {
  useDocumentTitle('System Health & Diagnostics');
  const [metrics, setMetrics] = useState<SystemHealthMetric[]>([]);
  const { resetDemoMode } = useCase();

  useEffect(() => {
    const fetchHealth = async () => {
      const data = await api.getSystemHealth();
      setMetrics(data);
    };
    fetchHealth();
  }, []);

  return (
    <div className="space-y-6 pb-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <HeartPulse className="w-7 h-7 text-primary-container" />
            System Health &amp; Diagnostics
          </h1>
          <p className="text-xs sm:text-sm text-on-surface-variant mt-1">
            Engine status, AI reasoning latency, Cisco CLI parsers, and demo state controller.
          </p>
        </div>

        <button
          onClick={resetDemoMode}
          className="px-4 py-2 rounded-lg text-xs font-mono font-bold bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40 flex items-center gap-2 transition-all active:scale-95 shadow-glow-warning"
        >
          <RotateCcw className="w-4 h-4" />
          <span>Reset All Mock State</span>
        </button>
      </div>

      {/* Health status cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {metrics.map((m: SystemHealthMetric, idx: number) => (
          <GlassCard key={idx} className="p-5 border border-white/10 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-emerald-500/20 flex items-center justify-center text-emerald-400">
                  <CheckCircle2 className="w-4 h-4" />
                </div>
                <h3 className="text-sm font-bold text-white font-sans">{m.name}</h3>
              </div>
              <StatusBadge status={m.status === 'OPERATIONAL' ? 'PASS' : 'WARNING'} size="sm" />
            </div>

            <div className="bg-black/30 p-3 rounded-lg border border-white/5 font-mono text-xs text-on-surface-variant">
              {m.value}
            </div>

            <div className="flex items-center justify-between text-[11px] font-mono text-outline">
              <span>Latency: <strong className="text-secondary">{m.latencyMs || 10} ms</strong></span>
              <span>Status: <strong className="text-emerald-400">Normal</strong></span>
            </div>
          </GlassCard>
        ))}
      </div>

      {/* Architecture overview */}
      <GlassDeep className="p-5 border border-white/10 space-y-3">
        <div className="flex items-center gap-2">
          <Cpu className="w-5 h-5 text-primary-container" />
          <h2 className="text-sm font-bold text-white">NetSage AI Architecture Specifications</h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs font-mono">
          <div className="bg-surface-container p-3 rounded-lg border border-white/5">
            <span className="text-outline block text-[10px]">BACKEND ENGINE</span>
            <span className="text-white font-bold">FastAPI + Python 3.11</span>
          </div>
          <div className="bg-surface-container p-3 rounded-lg border border-white/5">
            <span className="text-outline block text-[10px]">AI PROVIDERS</span>
            <span className="text-secondary font-bold">OpenAI / Gemini / Anthropic</span>
          </div>
          <div className="bg-surface-container p-3 rounded-lg border border-white/5">
            <span className="text-outline block text-[10px]">RULE ENGINE</span>
            <span className="text-emerald-400 font-bold">11 Deterministic Layer Rules</span>
          </div>
        </div>
      </GlassDeep>
    </div>
  );
};
