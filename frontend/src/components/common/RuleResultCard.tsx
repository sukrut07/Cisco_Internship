import React from 'react';
import { StatusBadge } from './StatusBadge';
import { RuleResult } from '../../types';
import { ShieldCheck, ShieldAlert, AlertCircle } from 'lucide-react';

export const RuleResultCard: React.FC<RuleResult> = ({
  name,
  status,
  layer,
  expected,
  actual,
  note
}) => {
  const borderColors = {
    PASS: 'border-l-4 border-l-emerald-400',
    FAIL: 'border-l-4 border-l-red-500',
    WARNING: 'border-l-4 border-l-amber-400'
  };

  const icons = {
    PASS: <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />,
    FAIL: <ShieldAlert className="w-4 h-4 text-red-400 shrink-0" />,
    WARNING: <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
  };

  return (
    <div
      className={`glass-card p-3.5 rounded-lg border border-white/5 ${borderColors[status]} flex flex-col gap-2 hover:bg-white/[0.03] transition-colors`}
    >
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          {icons[status]}
          <span className="font-mono text-xs font-semibold text-white truncate">
            {name}()
          </span>
          <span className="text-[10px] font-mono text-on-surface-variant bg-surface-container px-1.5 py-0.5 rounded border border-white/5">
            {layer}
          </span>
        </div>
        <StatusBadge status={status} size="sm" />
      </div>

      {(expected || actual) && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs font-mono bg-black/30 p-2.5 rounded border border-white/5">
          {expected && (
            <div>
              <span className="text-[10px] uppercase text-outline block">Expected:</span>
              <span className="text-emerald-300/90">{expected}</span>
            </div>
          )}
          {actual && (
            <div>
              <span className="text-[10px] uppercase text-outline block">Actual:</span>
              <span className={status === 'FAIL' ? 'text-red-400' : 'text-on-surface'}>
                {actual}
              </span>
            </div>
          )}
        </div>
      )}

      {note && (
        <p className="text-xs text-on-surface-variant leading-relaxed">
          {note}
        </p>
      )}
    </div>
  );
};
