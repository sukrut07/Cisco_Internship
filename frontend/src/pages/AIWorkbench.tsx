import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  AlertTriangle,
  Cpu,
  CheckCircle2,
  XCircle,
  FileCode,
  Layers,
  ArrowRight,
  ShieldCheck,
  Terminal,
  Activity,
  Check,
  Edit3
} from 'lucide-react';
import { useCase } from '../context/CaseContext';
import { GlassPanel, GlassCard, GlassDeep } from '../components/common/GlassWrappers';
import { StatusBadge } from '../components/common/StatusBadge';
import { ConfidenceMeter } from '../components/common/ConfidenceMeter';
import { CircularScoreGauge } from '../components/common/CircularScoreGauge';
import { TerminalWindow } from '../components/common/TerminalWindow';
import { RuleResultCard } from '../components/common/RuleResultCard';
import { SkeletonLoader } from '../components/common/SkeletonLoader';
import { useDocumentTitle } from '../hooks/useDocumentTitle';
import { EvidenceCitation, RuleResult } from '../types';

export const AIWorkbench: React.FC = () => {
  useDocumentTitle('AI Workbench');
  const { currentCase, loading, runDiagnosis, submitReview, approveFix } = useCase();
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isDiagnosing, setIsDiagnosing] = useState(false);

  const handleRunDiagnosis = async () => {
    if (!currentCase) return;
    try {
      setIsDiagnosing(true);
      await runDiagnosis(currentCase.case_id);
    } finally {
      setIsDiagnosing(false);
    }
  };

  useEffect(() => {
    if (currentCase?.show_outputs) {
      const keys = Object.keys(currentCase.show_outputs);
      if (keys.length > 0) {
        setActiveTab(keys[0]);
      }
    }
  }, [currentCase]);

  if (loading || !currentCase) {
    return (
      <div className="space-y-4">
        <SkeletonLoader className="h-16 w-full rounded-xl" />
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-4">
          <div className="xl:col-span-7 space-y-4">
            <SkeletonLoader className="h-64 w-full rounded-xl" />
            <SkeletonLoader className="h-48 w-full rounded-xl" />
          </div>
          <div className="xl:col-span-5 space-y-4">
            <SkeletonLoader className="h-96 w-full rounded-xl" />
          </div>
        </div>
      </div>
    );
  }

  const isConflict = currentCase.fusion_status === 'CONFLICT';
  const isReviewed = currentCase.status === 'ACCEPTED' || currentCase.status === 'EDITED' || currentCase.status === 'REJECTED' || currentCase.status === 'FIX_APPROVED' || currentCase.status === 'RESOLVED';

  const handleQuickAccept = async () => {
    try {
      setIsSubmitting(true);
      await submitReview(currentCase.case_id, {
        decision: 'ACCEPTED',
        reviewer: 'Lead Network Engineer',
        timestamp: new Date().toISOString(),
        notes: 'AI diagnosis and citations confirmed against IOS telemetry.'
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleQuickReject = async () => {
    try {
      setIsSubmitting(true);
      await submitReview(currentCase.case_id, {
        decision: 'REJECTED',
        reviewer: 'Lead Network Engineer',
        timestamp: new Date().toISOString(),
        notes: 'Rejected AI conclusion; forcing deterministic Rule Engine recommendation.',
        edited_root_cause: currentCase.rule_results.find((r: RuleResult) => r.status === 'FAIL')?.note || 'Manual override'
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-4 pb-8">
      {/* Top Banner: Conflict Detection (Only renders when fusion status is CONFLICT) */}
      {isConflict && (
        <div className="glass-panel p-4 rounded-xl border border-orange-500/50 bg-gradient-to-r from-orange-950/40 via-surface-container to-surface-container shadow-glow-critical flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 animate-fadeIn">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-orange-500/20 border border-orange-500/50 flex items-center justify-center shrink-0">
              <AlertTriangle className="w-5 h-5 text-primary" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-bold text-white tracking-wide">
                  AI &amp; RULE ENGINE CONFLICT DETECTED
                </h3>
                <span className="text-[10px] font-mono font-bold bg-orange-500/30 text-primary px-1.5 py-0.5 rounded border border-orange-500/40">
                  DISCREPANCY
                </span>
              </div>
              <p className="text-xs text-on-surface-variant mt-0.5">
                Deterministic rules flagged <strong>Layer 1 physical link state</strong>, while AI identified administrative interface suppression. Human validation required.
              </p>
            </div>
          </div>

          <button
            onClick={() => navigate('/review')}
            className="px-3.5 py-1.5 rounded-lg text-xs font-semibold font-mono bg-primary-container hover:bg-orange-500 text-white shadow-glow-critical shrink-0 flex items-center gap-1.5 transition-all"
          >
            <span>Resolve Conflict</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* Case Header & Badges */}
      <div className="glass-panel p-5 rounded-xl border border-white/10 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
        <div className="space-y-2">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-mono text-sm font-bold text-primary-container bg-primary-container/10 px-2 py-0.5 rounded border border-primary-container/30">
              {currentCase.case_id}
            </span>
            <StatusBadge status={currentCase.severity} size="sm" />
            <span className="font-mono text-xs text-secondary bg-secondary/10 px-2 py-0.5 rounded border border-secondary/30 flex items-center gap-1">
              <Layers className="w-3 h-3" />
              {currentCase.osi_layer}
            </span>
            <span className="font-sans text-xs font-semibold text-white/90 bg-white/10 px-2.5 py-0.5 rounded border border-white/10">
              {currentCase.concept}
            </span>
            <span className="font-mono text-xs text-on-surface-variant bg-surface-container px-2 py-0.5 rounded border border-white/5">
              Category: {currentCase.category}
            </span>
          </div>

          <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            {currentCase.title}
          </h1>

          <p className="text-xs sm:text-sm text-on-surface-variant leading-relaxed max-w-4xl">
            {currentCase.symptom}
          </p>
        </div>

        {/* Status Pill & Flow Progress */}
        <div className="flex flex-col items-start lg:items-end gap-2 shrink-0">
          <div className="flex items-center gap-2">
            <button
              onClick={handleRunDiagnosis}
              disabled={isDiagnosing}
              className="px-3 py-1.5 rounded-lg text-xs font-bold font-sans bg-primary-container hover:bg-orange-500 text-white shadow-glow-critical flex items-center gap-1.5 transition-all active:scale-95 disabled:opacity-50"
              title="Execute AI diagnosis and deterministic rule evaluation on current case telemetry"
            >
              <Cpu className={`w-3.5 h-3.5 ${isDiagnosing ? 'animate-spin' : ''}`} />
              <span>{isDiagnosing ? 'Analyzing...' : 'Run AI Diagnosis'}</span>
            </button>
            <StatusBadge status={currentCase.status} pulse={currentCase.status === 'REVIEW_REQUIRED'} />
          </div>
          <span className="text-[11px] font-mono text-outline">
            Topology: <code className="text-white/80">{currentCase.topology.split('->')[0]} ...</code>
          </span>
        </div>
      </div>

      {/* Dual Panel Split Layout */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-4">
        {/* Left Column (7 Cols): Telemetry, Command Outputs, Rule Engine, Evidence Citations */}
        <div className="xl:col-span-7 space-y-4">
          {/* Terminal Command Viewer */}
          <GlassPanel className="p-4 border border-white/10 flex flex-col gap-3">
            <div className="flex items-center justify-between flex-wrap gap-2">
              <div className="flex items-center gap-2">
                <Terminal className="w-4 h-4 text-primary-container" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-white">
                  Cisco IOS Command Outputs
                </h3>
              </div>

              {/* Tabs for show commands */}
              <div className="flex items-center gap-1.5 flex-wrap">
                {Object.keys(currentCase.show_outputs || {}).map((cmd) => (
                  <button
                    key={cmd}
                    onClick={() => setActiveTab(cmd)}
                    className={`px-2.5 py-1 text-xs font-mono rounded transition-colors ${
                      activeTab === cmd
                        ? 'bg-primary-container text-white font-semibold shadow-glow-critical'
                        : 'bg-surface-container text-on-surface-variant hover:text-white border border-white/5'
                    }`}
                  >
                    {cmd}
                  </button>
                ))}
              </div>
            </div>

            {/* Terminal Window with Typewriter Effect on Load */}
            {activeTab && currentCase.show_outputs[activeTab] && (
              <TerminalWindow
                key={activeTab}
                hostname="R1#"
                command={activeTab}
                title={`Telemetry Stream — ${activeTab}`}
                content={currentCase.show_outputs[activeTab]}
                enableTypewriter={true}
              />
            )}
          </GlassPanel>

          {/* Evidence Grounding Citations */}
          <GlassPanel className="p-4 border border-white/10 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileCode className="w-4 h-4 text-secondary" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-white">
                  Grounded Evidence Citations
                </h3>
              </div>
              <span className="text-[11px] font-mono text-secondary">
                {currentCase.ai_diagnosis.citations.length} Verified Sources
              </span>
            </div>

            <div className="space-y-2">
              {currentCase.ai_diagnosis.citations.map((cite: EvidenceCitation) => (
                <div
                  key={cite.id}
                  className="glass-card p-3 rounded-lg border border-secondary/20 bg-secondary/5 space-y-1.5"
                >
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className="text-secondary font-semibold flex items-center gap-1.5">
                      <Terminal className="w-3.5 h-3.5" />
                      {cite.source_command}
                    </span>
                    <span className="text-outline text-[11px]">{cite.line_numbers}</span>
                  </div>
                  <div className="bg-black/50 p-2 rounded border border-white/5 font-mono text-[11.5px] text-emerald-300">
                    {cite.snippet}
                  </div>
                  <p className="text-xs text-on-surface-variant font-sans">
                    <strong className="text-white">Significance:</strong> {cite.significance}
                  </p>
                </div>
              ))}
            </div>
          </GlassPanel>

          {/* Rule Engine Deterministic Checks */}
          <GlassPanel className="p-4 border border-white/10 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Activity className="w-4 h-4 text-amber-400" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-white">
                  Rule Engine Evaluation (Deterministic L1-L7)
                </h3>
              </div>
              <span className="text-[11px] font-mono text-outline">
                {currentCase.rule_results.length} Checks Run
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              {currentCase.rule_results.map((rule: RuleResult) => (
                <RuleResultCard key={rule.id} {...rule} />
              ))}
            </div>
          </GlassPanel>
        </div>

        {/* Right Column (5 Cols): AI Diagnosis, Metrics, Fix Plan & Human Gateway */}
        <div className="xl:col-span-5 space-y-4">
          {/* AI Root Cause Card */}
          <GlassDeep className="p-5 border border-primary-container/30 shadow-glow-critical space-y-4">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-md bg-primary-container/20 border border-primary-container/40 flex items-center justify-center">
                  <Cpu className="w-4 h-4 text-primary" />
                </div>
                <div>
                  <h2 className="text-sm font-bold text-white tracking-wide">
                    AI Grounded Diagnosis
                  </h2>
                  <span className="text-[10px] font-mono text-outline">
                    Model: Cisco-NetSage-Grounding-v2
                  </span>
                </div>
              </div>
              <span className="label-caps text-tertiary bg-emerald-950/40 px-2 py-0.5 rounded border border-emerald-500/30">
                Grounded
              </span>
            </div>

            {/* Root cause text */}
            <div className="bg-black/30 p-3.5 rounded-lg border border-white/5 space-y-1.5">
              <span className="label-caps text-primary block">Likely Root Cause</span>
              <p className="text-sm font-semibold text-white leading-snug">
                {currentCase.ai_diagnosis.root_cause}
              </p>
            </div>

            <p className="text-xs text-on-surface-variant leading-relaxed">
              {currentCase.ai_diagnosis.explanation}
            </p>

            {/* Confidence & Viability Score Gauge */}
            <div className="grid grid-cols-1 sm:grid-cols-12 gap-3 pt-2 border-t border-white/10 items-center">
              <div className="sm:col-span-7">
                <ConfidenceMeter value={currentCase.ai_diagnosis.confidence} />
                <div className="mt-3 text-[11px] font-mono text-outline">
                  Classification: <strong className="text-white">{currentCase.ai_diagnosis.osi_layer}</strong>
                </div>
              </div>
              <div className="sm:col-span-5 flex justify-center">
                <CircularScoreGauge
                  value={currentCase.ai_diagnosis.viability_score}
                  label="VIABILITY"
                  sublabel="System Support"
                  size={110}
                  strokeWidth={7}
                />
              </div>
            </div>

            {/* Recommended Fix Plan */}
            <div className="space-y-2 pt-2 border-t border-white/10">
              <span className="label-caps text-outline block">Recommended Remediation CLI</span>
              <div className="bg-[#0a0c10] p-3 rounded-lg border border-white/10 font-mono text-xs space-y-1 text-emerald-300">
                {currentCase.ai_diagnosis.recommended_fix.map((step: string, idx: number) => (
                  <div key={idx} className="flex items-center gap-2">
                    <span className="text-outline text-[10px] select-none">{idx + 1}.</span>
                    <span>{step}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Next Diagnostic Command */}
            <div className="bg-surface-container p-2.5 rounded-lg border border-white/5 flex items-center justify-between text-xs font-mono">
              <span className="text-outline text-[11px]">Next Diagnostic:</span>
              <code className="text-secondary font-bold">{currentCase.ai_diagnosis.next_command}</code>
            </div>
          </GlassDeep>

          {/* Mandatory Human-in-the-Loop Gateway */}
          <GlassPanel className="p-5 border border-primary-container/40 bg-gradient-to-b from-surface-container to-surface-container-high space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-primary-container" />
                <h3 className="text-sm font-bold text-white">
                  Human Gateway Decision
                </h3>
              </div>
              <span className="text-[10px] font-mono text-amber-300 bg-amber-950/40 px-2 py-0.5 rounded border border-amber-500/30">
                Mandatory Check
              </span>
            </div>

            <p className="text-xs text-on-surface-variant">
              In adherence to safety protocol, AI will never apply commands directly. Review and register your engineer authorization below.
            </p>

            {isReviewed ? (
              /* Already reviewed state */
              <div className="bg-emerald-950/30 p-4 rounded-xl border border-emerald-500/40 space-y-2 animate-fadeIn">
                <div className="flex items-center gap-2 text-emerald-300 font-semibold text-xs">
                  <Check className="w-4 h-4 text-emerald-400" />
                  <span>Review Decision Recorded: {currentCase.review?.decision || currentCase.status}</span>
                </div>
                <p className="text-xs text-on-surface-variant">
                  {currentCase.review?.notes || 'Decision submitted by authorized network engineer.'}
                </p>
                <div className="pt-2 flex items-center justify-between">
                  <span className="text-[11px] font-mono text-outline">
                    {currentCase.review?.reviewer || 'Lead Engineer'}
                  </span>
                  <button
                    onClick={() => navigate('/review')}
                    className="text-xs text-primary underline hover:text-primary-container font-mono"
                  >
                    View / Edit in Review Planner &rarr;
                  </button>
                </div>
              </div>
            ) : (
              /* Action Buttons */
              <div className="space-y-2">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  <button
                    onClick={handleQuickAccept}
                    disabled={isSubmitting}
                    aria-label="Accept AI diagnosis and fix plan"
                    className="px-3.5 py-2.5 rounded-lg text-xs font-bold font-sans bg-emerald-600 hover:bg-emerald-500 text-white shadow-glow-emerald flex items-center justify-center gap-1.5 transition-all duration-150 disabled:opacity-50 active:scale-95"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    <span>ACCEPT AI</span>
                  </button>

                  <button
                    onClick={handleQuickReject}
                    disabled={isSubmitting}
                    aria-label="Reject AI diagnosis and apply deterministic rule engine result"
                    className="px-3.5 py-2.5 rounded-lg text-xs font-bold font-sans bg-red-700/80 hover:bg-red-600 text-white border border-red-500/40 flex items-center justify-center gap-1.5 transition-all duration-150 disabled:opacity-50 active:scale-95"
                  >
                    <XCircle className="w-4 h-4" />
                    <span>REJECT &amp; FORCE RULE</span>
                  </button>
                </div>

                <button
                  onClick={() => navigate('/review')}
                  className="w-full py-2 rounded-lg text-xs font-semibold text-on-surface-variant hover:text-white bg-white/5 hover:bg-white/10 border border-white/10 flex items-center justify-center gap-2 transition-colors"
                >
                  <Edit3 className="w-3.5 h-3.5" />
                  <span>Open Full Review &amp; Fix Planner</span>
                </button>
              </div>
            )}
          </GlassPanel>
        </div>
      </div>
    </div>
  );
};
