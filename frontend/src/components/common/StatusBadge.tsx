import React from 'react';

export type BadgeStatus =
  | 'PASS'
  | 'FAIL'
  | 'WARNING'
  | 'CRITICAL'
  | 'UNKNOWN'
  | 'PENDING'
  | 'HIGH'
  | 'MEDIUM'
  | 'LOW'
  | 'RESOLVED'
  | 'ACCEPTED'
  | 'EDITED'
  | 'REJECTED'
  | 'REVIEW_REQUIRED'
  | 'FIX_APPROVED'
  | 'VERIFICATION';

interface StatusBadgeProps {
  status: string | BadgeStatus;
  size?: 'sm' | 'md';
  pulse?: boolean;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  size = 'md',
  pulse = false,
  className = ''
}) => {
  const norm = status?.toUpperCase() || 'UNKNOWN';

  let bgClass = 'bg-surface-container text-on-surface-variant border-white/10';
  let dotClass = 'bg-outline';
  let shadowClass = '';

  switch (norm) {
    case 'PASS':
    case 'RESOLVED':
    case 'ACCEPTED':
      bgClass = 'bg-emerald-950/50 text-emerald-300 border-emerald-500/40';
      dotClass = 'bg-emerald-400';
      shadowClass = 'shadow-glow-emerald';
      break;

    case 'FAIL':
    case 'REJECTED':
    case 'FAILED':
      bgClass = 'bg-red-950/50 text-red-300 border-red-500/40';
      dotClass = 'bg-red-400';
      break;

    case 'CRITICAL':
      bgClass = 'bg-orange-950/60 text-primary border-orange-500/60 shadow-glow-critical';
      dotClass = 'bg-primary-container';
      shadowClass = 'shadow-glow-critical';
      break;

    case 'HIGH':
      bgClass = 'bg-red-950/40 text-red-300 border-red-500/40';
      dotClass = 'bg-red-400';
      break;

    case 'WARNING':
    case 'MEDIUM':
    case 'REVIEW_REQUIRED':
    case 'EDITED':
      bgClass = 'bg-amber-950/50 text-amber-300 border-amber-500/40 shadow-glow-warning';
      dotClass = 'bg-amber-400';
      shadowClass = 'shadow-glow-warning';
      break;

    case 'LOW':
      bgClass = 'bg-slate-800/60 text-slate-300 border-slate-600/40';
      dotClass = 'bg-slate-400';
      break;

    case 'FIX_APPROVED':
    case 'VERIFICATION':
    case 'RUNNING':
      bgClass = 'bg-sky-950/50 text-secondary border-secondary/40 shadow-glow-cyan';
      dotClass = 'bg-secondary';
      shadowClass = 'shadow-glow-cyan';
      break;

    case 'PENDING':
    case 'UNKNOWN':
    default:
      bgClass = 'bg-surface-container-high text-on-surface-variant border-white/10';
      dotClass = 'bg-outline';
      break;
  }

  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-[10px]' : 'px-2.5 py-1 text-[11px]';

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-bold uppercase tracking-wider rounded border font-mono ${sizeClasses} ${bgClass} ${shadowClass} ${className}`}
    >
      <span
        className={`w-1.5 h-1.5 rounded-full ${dotClass} ${pulse ? 'animate-pulse-indicator' : ''}`}
      />
      {norm.replace(/_/g, ' ')}
    </span>
  );
};
