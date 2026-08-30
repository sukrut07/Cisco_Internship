import React, { useState, useEffect } from 'react';
import {
  History,
  ShieldCheck,
  Cpu,
  FileCheck,
  CheckCircle2,
  AlertTriangle,
  Play,
  Terminal,
  Search,
  Filter
} from 'lucide-react';
import { api } from '../services/api';
import { AuditLogEntry } from '../types';
import { GlassPanel, GlassDeep } from '../components/common/GlassWrappers';
import { StatusBadge } from '../components/common/StatusBadge';
import { SkeletonLoader } from '../components/common/SkeletonLoader';
import { useDocumentTitle } from '../hooks/useDocumentTitle';

export const AuditLogPage: React.FC = () => {
  useDocumentTitle('Audit & Compliance Trail');
  const [logs, setLogs] = useState<AuditLogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('ALL');

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        setLoading(true);
        const data = await api.getAuditLogs();
        setLogs(data);
      } finally {
        setLoading(false);
      }
    };
    fetchLogs();
  }, []);

  const actionIcons: Record<string, React.ReactNode> = {
    CASE_CREATED: <Terminal className="w-4 h-4 text-secondary" />,
    RULE_ENGINE_EVALUATED: <ShieldCheck className="w-4 h-4 text-amber-400" />,
    DIAGNOSIS_GENERATED: <Cpu className="w-4 h-4 text-primary-container" />,
    REVIEW_STARTED: <AlertTriangle className="w-4 h-4 text-amber-400" />,
    REVIEW_DECISION_RECORDED: <FileCheck className="w-4 h-4 text-emerald-400" />,
    FIX_PLAN_APPROVED: <CheckCircle2 className="w-4 h-4 text-emerald-400" />,
    VERIFICATION_EXECUTED: <Play className="w-4 h-4 text-cyan-400" />,
    CASE_RESOLVED: <CheckCircle2 className="w-4 h-4 text-emerald-400" />
  };

  const filteredLogs = logs.filter(log => {
    if (search.trim()) {
      const q = search.toLowerCase();
      const match =
        log.actor.toLowerCase().includes(q) ||
        log.details.toLowerCase().includes(q) ||
        (log.case_id && log.case_id.toLowerCase().includes(q)) ||
        log.action_type.toLowerCase().includes(q);
      if (!match) return false;
    }
    if (typeFilter !== 'ALL' && log.action_type !== typeFilter) {
      return false;
    }
    return true;
  });

  return (
    <div className="space-y-6 pb-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <History className="w-7 h-7 text-primary-container" />
            Compliance &amp; Operational Audit Trail
          </h1>
          <p className="text-xs sm:text-sm text-on-surface-variant mt-1">
            Immutable log of all AI inferences, deterministic rule evaluations, and human engineer approvals.
          </p>
        </div>
      </div>

      {/* Filter Bar */}
      <GlassPanel className="p-4 border border-white/10 flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-outline absolute left-3 top-2.5 pointer-events-none" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search audit trail by actor, case ID, or event details..."
            className="w-full bg-surface-container pl-9 pr-4 py-2 text-xs text-white rounded-lg border border-white/10 focus:border-primary-container focus:outline-none font-sans"
          />
        </div>

        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-outline" />
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="bg-surface-container text-xs text-white px-3 py-2 rounded-lg border border-white/10 focus:border-primary-container font-mono"
          >
            <option value="ALL">All Event Types</option>
            <option value="CASE_CREATED">CASE_CREATED</option>
            <option value="RULE_ENGINE_EVALUATED">RULE_ENGINE_EVALUATED</option>
            <option value="DIAGNOSIS_GENERATED">DIAGNOSIS_GENERATED</option>
            <option value="REVIEW_DECISION_RECORDED">REVIEW_DECISION_RECORDED</option>
            <option value="FIX_PLAN_APPROVED">FIX_PLAN_APPROVED</option>
            <option value="CASE_RESOLVED">CASE_RESOLVED</option>
          </select>
        </div>
      </GlassPanel>

      {/* Timeline List */}
      <GlassDeep className="p-5 border border-white/10 space-y-4">
        {loading ? (
          <SkeletonLoader className="h-64 rounded-xl" />
        ) : filteredLogs.length === 0 ? (
          <div className="text-center py-12 text-outline text-xs">
            No audit records found matching query.
          </div>
        ) : (
          <div className="relative border-l border-white/10 ml-4 space-y-6 py-2">
            {filteredLogs.map((log) => (
              <div key={log.id} className="relative pl-6 group">
                {/* Node icon marker */}
                <div className="absolute -left-3 top-0.5 w-6 h-6 rounded-full bg-surface-container border border-white/20 flex items-center justify-center group-hover:border-primary-container transition-colors">
                  {actionIcons[log.action_type] || <Terminal className="w-3.5 h-3.5 text-outline" />}
                </div>

                <div className="glass-card p-4 rounded-xl border border-white/5 space-y-2">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-mono text-xs font-bold text-white">
                        {log.action_type}
                      </span>
                      {log.case_id && (
                        <span className="font-mono text-[11px] text-primary bg-primary/10 px-2 py-0.5 rounded border border-primary/20">
                          {log.case_id}
                        </span>
                      )}
                    </div>
                    <span className="font-mono text-[11px] text-outline">
                      {new Date(log.timestamp).toLocaleString()}
                    </span>
                  </div>

                  <p className="text-xs text-on-surface-variant font-sans leading-relaxed">
                    {log.details}
                  </p>

                  <div className="flex items-center justify-between text-[11px] font-mono pt-1 border-t border-white/5">
                    <span className="text-outline">
                      Actor: <strong className="text-white">{log.actor}</strong>
                    </span>
                    <StatusBadge status={log.status === 'SUCCESS' ? 'PASS' : log.status} size="sm" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </GlassDeep>
    </div>
  );
};
