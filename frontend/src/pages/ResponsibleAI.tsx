import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  AlertTriangle,
  Scale,
  BrainCircuit,
  ArrowUpDown,
  Lock
} from 'lucide-react';
import { api } from '../services/api';
import { ResponsibleAIMismatch } from '../types';
import { GlassCard, GlassDeep } from '../components/common/GlassWrappers';
import { StatusBadge } from '../components/common/StatusBadge';
import { SkeletonLoader } from '../components/common/SkeletonLoader';
import { useDocumentTitle } from '../hooks/useDocumentTitle';

export const ResponsibleAI: React.FC = () => {
  useDocumentTitle('Responsible AI & Human Alignment');
  const [mismatches, setMismatches] = useState<ResponsibleAIMismatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortField, setSortField] = useState<'case_id' | 'confidence'>('case_id');
  const [sortAsc, setSortAsc] = useState(true);

  useEffect(() => {
    const fetchMismatches = async () => {
      try {
        setLoading(true);
        const data = await api.getResponsibleAIMismatches();
        setMismatches(data);
      } finally {
        setLoading(false);
      }
    };
    fetchMismatches();
  }, []);

  const sortedMismatches = [...mismatches].sort((a, b) => {
    if (sortField === 'confidence') {
      return sortAsc ? a.confidence - b.confidence : b.confidence - a.confidence;
    }
    return sortAsc ? a.case_id.localeCompare(b.case_id) : b.case_id.localeCompare(a.case_id);
  });

  return (
    <div className="space-y-6 pb-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <ShieldCheck className="w-7 h-7 text-primary-container" />
            Responsible AI &amp; Human Alignment
          </h1>
          <p className="text-xs sm:text-sm text-on-surface-variant mt-1">
            Tracking AI diagnosis discrepancies, human correction justifications, and safety guardrails.
          </p>
        </div>
      </div>

      {/* Safety Policy Pillars */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <GlassCard className="p-4 border border-white/10 space-y-2">
          <div className="flex items-center gap-2 text-primary">
            <Lock className="w-5 h-5 text-primary-container" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-white">
              Zero Autonomous Execution
            </h3>
          </div>
          <p className="text-xs text-on-surface-variant leading-relaxed">
            NetSage AI strictly prevents direct CLI command execution. All network remediations require explicit human engineer review.
          </p>
        </GlassCard>

        <GlassCard className="p-4 border border-white/10 space-y-2">
          <div className="flex items-center gap-2 text-secondary">
            <BrainCircuit className="w-5 h-5 text-secondary" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-white">
              Evidence-Grounded Reasoning
            </h3>
          </div>
          <p className="text-xs text-on-surface-variant leading-relaxed">
            Every diagnosed root-cause must cite exact line numbers from supplied Cisco <code className="text-white">show</code> command telemetry.
          </p>
        </GlassCard>

        <GlassCard className="p-4 border border-white/10 space-y-2">
          <div className="flex items-center gap-2 text-tertiary">
            <Scale className="w-5 h-5 text-tertiary" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-white">
              Continuous Calibration
            </h3>
          </div>
          <p className="text-xs text-on-surface-variant leading-relaxed">
            Human engineer overrides are logged and indexed to recalibrate prompting schemas and rule confidence weighting.
          </p>
        </GlassCard>
      </div>

      {/* Discrepancy & Correction Ledger */}
      <GlassDeep className="p-5 border border-white/10 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            <div>
              <h2 className="text-sm font-bold text-white tracking-wide">
                AI vs Human Diagnosis Discrepancy Ledger
              </h2>
              <span className="text-[11px] font-mono text-outline">
                {mismatches.length} Human Corrections Recorded
              </span>
            </div>
          </div>
        </div>

        {loading ? (
          <SkeletonLoader className="h-64 rounded-xl" />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-white/10 text-outline select-none">
                  <th
                    onClick={() => {
                      setSortField('case_id');
                      setSortAsc(!sortAsc);
                    }}
                    className="pb-3 font-semibold cursor-pointer hover:text-white"
                  >
                    <div className="flex items-center gap-1">
                      <span>CASE ID</span>
                      <ArrowUpDown className="w-3 h-3" />
                    </div>
                  </th>
                  <th className="pb-3 font-semibold">AI PROPOSED DIAGNOSIS</th>
                  <th className="pb-3 font-semibold">DECISION</th>
                  <th className="pb-3 font-semibold">HUMAN CORRECTED DIAGNOSIS</th>
                  <th className="pb-3 font-semibold">CORRECTION RATIONALE</th>
                  <th
                    onClick={() => {
                      setSortField('confidence');
                      setSortAsc(!sortAsc);
                    }}
                    className="pb-3 font-semibold cursor-pointer hover:text-white text-right"
                  >
                    <div className="flex items-center gap-1 justify-end">
                      <span>AI CONF</span>
                      <ArrowUpDown className="w-3 h-3" />
                    </div>
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {sortedMismatches.map((m) => (
                  <tr key={m.id} className="hover:bg-white/[0.03] transition-colors">
                    <td className="py-3.5 font-bold text-primary-container whitespace-nowrap">
                      {m.case_id}
                    </td>
                    <td className="py-3.5 text-on-surface-variant font-sans max-w-xs pr-4">
                      {m.ai_root_cause}
                    </td>
                    <td className="py-3.5 whitespace-nowrap">
                      <StatusBadge status={m.human_decision} size="sm" />
                    </td>
                    <td className="py-3.5 text-emerald-300 font-sans font-medium max-w-xs pr-4">
                      {m.human_root_cause}
                    </td>
                    <td className="py-3.5 text-on-surface-variant font-sans max-w-sm pr-4">
                      {m.correction_reason}
                    </td>
                    <td className="py-3.5 text-right font-bold text-white whitespace-nowrap">
                      {m.confidence}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </GlassDeep>
    </div>
  );
};
