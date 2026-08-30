import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ShieldCheck,
  CheckCircle2,
  XCircle,
  Edit3,
  ArrowRight,
  FileCheck,
  Plus,
  Trash2,
  Terminal,
  Sparkles
} from 'lucide-react';
import { useCase } from '../context/CaseContext';
import { useReviewFlow } from '../hooks/useReviewFlow';
import { GlassPanel, GlassDeep } from '../components/common/GlassWrappers';
import { StatusBadge } from '../components/common/StatusBadge';
import { useDocumentTitle } from '../hooks/useDocumentTitle';

export const ReviewPage: React.FC = () => {
  useDocumentTitle('Human Review & Fix Planner');
  const { currentCase } = useCase();
  const navigate = useNavigate();

  const {
    decision,
    setDecision,
    reviewerName,
    setReviewerName,
    notes,
    setNotes,
    editedRootCause,
    setEditedRootCause,
    fixSteps,
    newStep,
    setNewStep,
    addFixStep,
    removeFixStep,
    isSubmitting,
    isApproved,
    hasDecision,
    handleRecordReview,
    handleApproveFix
  } = useReviewFlow(currentCase);

  if (!currentCase) {
    return (
      <div className="p-8 text-center glass-panel rounded-xl">
        <h2 className="text-lg font-bold text-white">No Active Case Selected</h2>
        <p className="text-xs text-on-surface-variant mt-2">Please select a case from the Explorer.</p>
        <button
          onClick={() => navigate('/cases')}
          className="mt-4 px-4 py-2 bg-primary-container text-white rounded-lg text-xs font-mono"
        >
          Go to Cases
        </button>
      </div>
    );
  }

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
            <span className="text-xs font-semibold text-white/90 bg-white/10 px-2 py-0.5 rounded">
              {currentCase.concept}
            </span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Human-in-the-Loop Review &amp; Fix Authorization
          </h1>
          <p className="text-xs text-on-surface-variant">
            Safety protocol checkpoint. Authorize or revise the AI-generated remediation commands before staging.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <StatusBadge status={currentCase.status} />
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
        {/* Left Column (6 Cols): Review Decision & Diagnosis Verification */}
        <div className="xl:col-span-6 space-y-4">
          <GlassDeep className="p-5 border border-white/10 space-y-4">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-primary-container" />
                <h2 className="text-sm font-bold text-white tracking-wide">
                  1. Review Assessment &amp; Authorization
                </h2>
              </div>
              <span className="label-caps text-outline">Step 1 of 2</span>
            </div>

            {/* Decision selector radio group */}
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => setDecision('ACCEPTED')}
                className={`p-3 rounded-lg border flex flex-col items-center gap-1.5 transition-all text-xs font-bold ${
                  decision === 'ACCEPTED'
                    ? 'bg-emerald-950/60 border-emerald-500 text-emerald-300 shadow-glow-emerald'
                    : 'bg-surface-container border-white/10 text-on-surface-variant hover:text-white'
                }`}
                aria-label="Accept AI diagnosis and fix"
              >
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                <span>ACCEPT AI</span>
              </button>

              <button
                type="button"
                onClick={() => setDecision('EDITED')}
                className={`p-3 rounded-lg border flex flex-col items-center gap-1.5 transition-all text-xs font-bold ${
                  decision === 'EDITED'
                    ? 'bg-amber-950/60 border-amber-500 text-amber-300 shadow-glow-warning'
                    : 'bg-surface-container border-white/10 text-on-surface-variant hover:text-white'
                }`}
                aria-label="Edit AI diagnosis and fix steps"
              >
                <Edit3 className="w-5 h-5 text-amber-400" />
                <span>EDIT / TWEAK</span>
              </button>

              <button
                type="button"
                onClick={() => setDecision('REJECTED')}
                className={`p-3 rounded-lg border flex flex-col items-center gap-1.5 transition-all text-xs font-bold ${
                  decision === 'REJECTED'
                    ? 'bg-red-950/60 border-red-500 text-red-300'
                    : 'bg-surface-container border-white/10 text-on-surface-variant hover:text-white'
                }`}
                aria-label="Reject AI diagnosis"
              >
                <XCircle className="w-5 h-5 text-red-400" />
                <span>REJECT</span>
              </button>
            </div>

            {/* Reviewer Name */}
            <div className="space-y-1.5 text-xs font-mono">
              <label className="text-outline text-[11px]">Authorizing Engineer Name / ID:</label>
              <input
                type="text"
                value={reviewerName}
                onChange={(e) => setReviewerName(e.target.value)}
                className="w-full bg-surface-container px-3 py-2 text-white rounded-lg border border-white/10 focus:border-primary-container focus:outline-none"
                aria-label="Authorizing engineer name"
              />
            </div>

            {/* Root Cause (Editable if EDITED) */}
            <div className="space-y-1.5 text-xs font-mono">
              <label className="text-outline text-[11px]">Grounded Root Cause Diagnostic:</label>
              {decision === 'EDITED' ? (
                <textarea
                  value={editedRootCause}
                  onChange={(e) => setEditedRootCause(e.target.value)}
                  rows={3}
                  className="w-full bg-surface-container px-3 py-2 text-white text-xs font-sans rounded-lg border border-amber-500/50 focus:border-amber-400 focus:outline-none"
                  aria-label="Edited root cause"
                />
              ) : (
                <div className="bg-black/30 p-3 rounded-lg border border-white/5 text-white font-sans text-xs leading-relaxed">
                  {currentCase.ai_diagnosis.root_cause}
                </div>
              )}
            </div>

            {/* Review Notes / Rationale */}
            <div className="space-y-1.5 text-xs font-mono">
              <label className="text-outline text-[11px]">Engineer Notes &amp; Rationale:</label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Document your verification findings, rule comparison, or specific lab topology nuances..."
                rows={3}
                className="w-full bg-surface-container px-3 py-2 text-white text-xs font-sans rounded-lg border border-white/10 focus:border-primary-container focus:outline-none"
                aria-label="Engineer notes and rationale"
              />
            </div>

            {/* Submit Review Button */}
            <button
              type="button"
              onClick={handleRecordReview}
              disabled={isSubmitting}
              className="w-full py-2.5 rounded-lg text-xs font-bold font-sans bg-primary-container hover:bg-orange-500 text-white shadow-glow-critical flex items-center justify-center gap-2 transition-all active:scale-95 disabled:opacity-50"
              aria-label="Record review decision in audit trail"
            >
              <FileCheck className="w-4 h-4" />
              <span>Record Review Decision</span>
            </button>
          </GlassDeep>
        </div>

        {/* Right Column (6 Cols): Fix Sequence Planner & Live Approval */}
        <div className="xl:col-span-6 space-y-4">
          <GlassDeep className="p-5 border border-white/10 space-y-4">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <div className="flex items-center gap-2">
                <Terminal className="w-5 h-5 text-secondary" />
                <h2 className="text-sm font-bold text-white tracking-wide">
                  2. Staged Remediation Sequence
                </h2>
              </div>
              <span className="label-caps text-outline">Step 2 of 2</span>
            </div>

            <p className="text-xs text-on-surface-variant">
              CLI commands to be staged into the automated Packet Tracer verification executor:
            </p>

            {/* Steps List */}
            <div className="space-y-2 max-h-[300px] overflow-y-auto">
              {fixSteps.map((step, idx) => (
                <div
                  key={idx}
                  className="bg-[#0a0c10] p-2.5 rounded-lg border border-white/10 flex items-center justify-between gap-2 font-mono text-xs text-emerald-300"
                >
                  <div className="flex items-center gap-2 overflow-hidden">
                    <span className="text-outline text-[10px] w-4 select-none">{idx + 1}.</span>
                    <span className="truncate">{step}</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => removeFixStep(idx)}
                    className="text-on-surface-variant hover:text-red-400 p-1"
                    title={`Remove command ${step}`}
                    aria-label={`Remove command ${step}`}
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>

            {/* Add Step Input */}
            <div className="flex items-center gap-2 pt-2 border-t border-white/5 font-mono text-xs">
              <input
                type="text"
                value={newStep}
                onChange={(e) => setNewStep(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') addFixStep();
                }}
                placeholder="Enter additional Cisco IOS command (e.g. no shutdown)..."
                className="flex-1 bg-surface-container px-3 py-2 text-white rounded-lg border border-white/10 focus:border-secondary focus:outline-none"
                aria-label="Add new remediation command"
              />
              <button
                type="button"
                onClick={addFixStep}
                className="px-3 py-2 bg-white/10 hover:bg-white/15 text-white rounded-lg border border-white/10 flex items-center gap-1 font-sans text-xs font-semibold"
                aria-label="Add command to fix plan"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Add</span>
              </button>
            </div>

            {/* Approve Fix CTA */}
            <div className="pt-4 border-t border-white/10 space-y-3">
              <button
                type="button"
                onClick={handleApproveFix}
                disabled={!hasDecision || isApproved || isSubmitting}
                className={`w-full py-3 rounded-lg text-xs font-bold font-sans flex items-center justify-center gap-2 transition-all ${
                  isApproved
                    ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-500/40 cursor-default'
                    : hasDecision
                    ? 'bg-gradient-to-r from-primary-container to-orange-600 text-white shadow-glow-critical hover:brightness-110 active:scale-95'
                    : 'bg-white/5 text-outline cursor-not-allowed border border-white/5'
                }`}
                aria-label="Approve and stage fix plan"
              >
                {isApproved ? (
                  <>
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    <span>Fix Plan Approved &amp; Staged</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Approve &amp; Stage Fix Plan</span>
                  </>
                )}
              </button>

              {/* Proceed to verification button */}
              {isApproved && (
                <button
                  type="button"
                  onClick={() => navigate('/verification')}
                  className="w-full py-2.5 rounded-lg text-xs font-bold font-sans bg-cyan-600 hover:bg-cyan-500 text-white shadow-glow-cyan flex items-center justify-center gap-2 transition-all animate-fadeIn active:scale-95"
                  aria-label="Proceed to live verification suite"
                >
                  <span>Proceed to Live Verification</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              )}
            </div>
          </GlassDeep>
        </div>
      </div>
    </div>
  );
};
