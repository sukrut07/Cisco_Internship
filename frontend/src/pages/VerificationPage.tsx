import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Play,
  Terminal,
  Activity,
  ArrowRight,
  RotateCcw,
  Sparkles,
  Zap
} from 'lucide-react';
import { useCase } from '../context/CaseContext';
import { GlassPanel, GlassDeep } from '../components/common/GlassWrappers';
import { StatusBadge } from '../components/common/StatusBadge';
import { VerificationCheck } from '../types';
import { useDocumentTitle } from '../hooks/useDocumentTitle';

export const VerificationPage: React.FC = () => {
  useDocumentTitle('Live Verification Probes');
  const { currentCase, runVerification, resetDemoMode } = useCase();
  const navigate = useNavigate();
  const [isRunning, setIsRunning] = useState(false);

  if (!currentCase) {
    return (
      <div className="p-8 text-center glass-panel rounded-xl">
        <h2 className="text-lg font-bold text-white">No Active Case Selected</h2>
        <button
          onClick={() => navigate('/cases')}
          className="mt-4 px-4 py-2 bg-primary-container text-white rounded-lg text-xs font-mono"
        >
          Go to Cases
        </button>
      </div>
    );
  }

  const isResolved = currentCase.status === 'RESOLVED';
  const isFixApproved = currentCase.status === 'FIX_APPROVED' || isResolved || currentCase.status === 'VERIFICATION';

  const handleStartVerification = async () => {
    try {
      setIsRunning(true);
      await runVerification(currentCase.case_id);
    } finally {
      setIsRunning(false);
    }
  };

  const checks: VerificationCheck[] = currentCase.verification?.checks || [
    {
      id: 'vcheck-1',
      description: 'Interface Physical & Line Protocol Status Check',
      target_device: currentCase.devices?.[2]?.name || 'R1 (Core Router)',
      command: 'show ip interface brief',
      status: 'PENDING'
    },
    {
      id: 'vcheck-2',
      description: 'End-to-End ICMP Echo Verification (5/5 packets)',
      target_device: 'PC1 (Source Host)',
      command: 'ping 10.0.0.100 repeat 5',
      status: 'PENDING'
    },
    {
      id: 'vcheck-3',
      description: 'Forwarding Path & Routing Consistency Validation',
      target_device: 'R1 / Core Gateway',
      command: 'show ip route',
      status: 'PENDING'
    }
  ];

  return (
    <div className="space-y-6 pb-8">
      {/* Header */}
      <div className="glass-panel p-5 rounded-xl border border-white/10 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="font-mono text-sm font-bold text-primary-container bg-primary-container/10 px-2 py-0.5 rounded border border-primary-container/30">
              {currentCase.case_id}
            </span>
            <StatusBadge status={currentCase.severity} size="sm" />
            <span className="text-xs font-mono text-secondary bg-secondary/10 px-2 py-0.5 rounded border border-secondary/30">
              {currentCase.osi_layer}
            </span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Automated Live Verification Suite
          </h1>
          <p className="text-xs text-on-surface-variant">
            Run deterministic Packet Tracer diagnostic checks to validate circuit restoration and packet flow.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <StatusBadge status={currentCase.status} pulse={isRunning} />
        </div>
      </div>

      {/* Final Resolved Banner if all checks passed */}
      {isResolved && (
        <div className="glass-panel p-6 rounded-xl border border-emerald-500/50 bg-gradient-to-r from-emerald-950/40 via-surface-container to-surface-container shadow-glow-emerald animate-fadeIn flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/20 border border-emerald-500/50 flex items-center justify-center text-emerald-400 shrink-0 shadow-glow-emerald">
              <Sparkles className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-white tracking-wide">
                  CASE VERIFIED &amp; RESOLVED
                </h2>
                <span className="text-[10px] font-mono font-bold bg-emerald-500/30 text-emerald-300 px-2 py-0.5 rounded border border-emerald-500/40">
                  ALL PASS
                </span>
              </div>
              <p className="text-xs text-on-surface-variant mt-1">
                End-to-end network connectivity validated across all hops. Incident closed and archived into the audit trail.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={() => navigate('/audit')}
              className="px-3.5 py-2 rounded-lg text-xs font-mono font-semibold bg-white/10 hover:bg-white/15 text-white border border-white/10 transition-colors"
            >
              View Audit Log
            </button>
            <button
              onClick={() => navigate('/cases')}
              className="px-4 py-2 rounded-lg text-xs font-bold font-sans bg-emerald-600 hover:bg-emerald-500 text-white shadow-glow-emerald flex items-center gap-1.5 transition-all"
            >
              <span>Next Case</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Main Verification Execution Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
        {/* Verification Check Suite (7 Cols) */}
        <div className="xl:col-span-7 space-y-4">
          <GlassDeep className="p-5 border border-white/10 space-y-4">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <div className="flex items-center gap-2">
                <Activity className="w-5 h-5 text-secondary" />
                <h2 className="text-sm font-bold text-white tracking-wide">
                  Diagnostic Probes &amp; Ping Matrix
                </h2>
              </div>
              <span className="text-[11px] font-mono text-outline">
                {checks.filter((c: VerificationCheck) => c.status === 'PASS').length} of {checks.length} Passed
              </span>
            </div>

            {/* Check Cards */}
            <div className="space-y-3">
              {checks.map((check: VerificationCheck, idx: number) => {
                const borderColors: Record<string, string> = {
                  PASS: 'border-emerald-500/40 bg-emerald-950/20 shadow-glow-emerald',
                  FAIL: 'border-red-500/40 bg-red-950/20',
                  RUNNING: 'border-secondary/40 bg-secondary/10 animate-pulse',
                  PENDING: 'border-white/5 bg-surface-container'
                };

                const cardClass = borderColors[check.status] || 'border-white/5 bg-surface-container';

                return (
                  <div
                    key={check.id || idx}
                    className={`p-4 rounded-xl border transition-all ${cardClass}`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-2.5">
                        <span className="w-5 h-5 rounded-full bg-white/10 flex items-center justify-center text-xs font-mono text-outline">
                          {idx + 1}
                        </span>
                        <div>
                          <h3 className="text-xs font-bold text-white font-sans">
                            {check.description}
                          </h3>
                          <span className="text-[11px] font-mono text-on-surface-variant">
                            Target: <code className="text-secondary">{check.target_device}</code>
                          </span>
                        </div>
                      </div>

                      <StatusBadge status={check.status} size="sm" pulse={check.status === 'RUNNING'} />
                    </div>

                    {/* Command and snippet */}
                    <div className="mt-3 bg-black/40 p-2.5 rounded-lg border border-white/5 font-mono text-xs space-y-1">
                      <div className="text-outline text-[11px] flex items-center gap-1.5">
                        <Terminal className="w-3.5 h-3.5 text-primary" />
                        <span>Command:</span>
                        <code className="text-primary-container font-bold">{check.command}</code>
                      </div>
                      {check.output_snippet && (
                        <div className="text-emerald-300 text-[11.5px] pt-1 border-t border-white/5">
                          &gt; {check.output_snippet}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Launch Verification Button */}
            <div className="pt-3 border-t border-white/10">
              <button
                onClick={handleStartVerification}
                disabled={!isFixApproved || isRunning}
                className={`w-full py-3 rounded-lg text-xs font-bold font-sans flex items-center justify-center gap-2 transition-all ${
                  !isFixApproved
                    ? 'bg-white/5 text-outline border border-white/5 cursor-not-allowed'
                    : isRunning
                    ? 'bg-secondary/20 text-secondary border border-secondary/30 animate-pulse cursor-wait'
                    : isResolved
                    ? 'bg-white/10 hover:bg-white/15 text-white border border-white/10'
                    : 'bg-gradient-to-r from-cyan-500 to-secondary text-slate-950 shadow-glow-cyan hover:brightness-110 active:scale-95'
                }`}
              >
                {isRunning ? (
                  <>
                    <Activity className="w-4 h-4 animate-spin" />
                    <span>Executing Probes Across Virtual Network...</span>
                  </>
                ) : isResolved ? (
                  <>
                    <RotateCcw className="w-4 h-4" />
                    <span>Re-Run Verification Suite</span>
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 fill-current" />
                    <span>Run Verification Probes Live</span>
                  </>
                )}
              </button>

              {!isFixApproved && (
                <p className="text-[11px] text-amber-400/90 text-center mt-2 font-mono">
                  * Fix plan must be reviewed and approved before live verification can be executed.
                </p>
              )}
            </div>
          </GlassDeep>
        </div>

        {/* Right Column (5 Cols): Staged Commands & Topology Context */}
        <div className="xl:col-span-5 space-y-4">
          {/* Staged Fix Commands */}
          <GlassPanel className="p-5 border border-white/10 space-y-3">
            <div className="flex items-center gap-2">
              <Terminal className="w-4 h-4 text-emerald-400" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-white">
                Executed Remediation Script
              </h3>
            </div>
            <div className="bg-[#0a0c10] p-3 rounded-lg border border-white/10 font-mono text-xs space-y-1.5 text-emerald-300">
              {(currentCase.review?.edited_fix || currentCase.ai_diagnosis.recommended_fix).map((step: string, i: number) => (
                <div key={i} className="flex items-center gap-2">
                  <span className="text-outline text-[10px] select-none">{i + 1}.</span>
                  <span>{step}</span>
                </div>
              ))}
            </div>
          </GlassPanel>

          {/* Topology Snapshot */}
          <GlassPanel className="p-5 border border-white/10 space-y-3">
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-primary" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-white">
                Target Lab Topology
              </h3>
            </div>
            <div className="bg-surface-container p-3 rounded-lg border border-white/5 font-mono text-xs text-on-surface-variant leading-relaxed">
              {currentCase.topology}
            </div>
          </GlassPanel>

          {/* Reset Demo CTA for judges */}
          <div className="p-4 rounded-xl glass-card border border-amber-500/20 flex items-center justify-between">
            <div className="flex flex-col">
              <span className="text-xs font-bold text-amber-300">Live Demo Replay</span>
              <span className="text-[10px] text-on-surface-variant">Reset case to re-run for judges</span>
            </div>
            <button
              onClick={resetDemoMode}
              className="px-3 py-1.5 rounded-lg text-xs font-mono font-semibold bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/30 transition-colors"
            >
              Reset State
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
