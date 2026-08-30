import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, ShieldAlert } from 'lucide-react';

export default function RuleCheckBadges({ ruleChecks = [] }) {
  if (!ruleChecks || ruleChecks.length === 0) {
    return (
      <div style={{ padding: '1rem', background: '#0f172a', borderRadius: '0.5rem', border: '1px solid #1e293b', textAlign: 'center', color: '#64748b', fontSize: '0.85rem' }}>
        No deterministic rule checks executed yet. Run rule checker to analyze packet outputs.
      </div>
    );
  }

  const failedChecks = ruleChecks.filter(r => r.status === 'failed');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <h4 style={{ fontSize: '0.9rem', fontWeight: '700', color: '#f1f5f9', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <ShieldAlert size={16} color="#06b6d4" />
          <span>Deterministic Python Findings ({ruleChecks.length})</span>
        </h4>
        <span style={{ fontSize: '0.75rem', fontWeight: '600', color: failedChecks.length > 0 ? '#f43f5e' : '#10b981' }}>
          {failedChecks.length > 0 ? `${failedChecks.length} Rule Failures` : 'All Rule Checks Passed'}
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        {ruleChecks.map((rc, idx) => {
          const isFailed = rc.status === 'failed';
          return (
            <div
              key={idx}
              style={{
                background: isFailed ? 'rgba(244, 63, 94, 0.08)' : 'rgba(16, 185, 129, 0.05)',
                border: isFailed ? '1px solid rgba(244, 63, 94, 0.3)' : '1px solid rgba(16, 185, 129, 0.2)',
                borderRadius: '0.5rem',
                padding: '0.75rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.35rem'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  {isFailed ? (
                    <XCircle size={16} color="#f43f5e" />
                  ) : (
                    <CheckCircle2 size={16} color="#10b981" />
                  )}
                  <span style={{ fontSize: '0.85rem', fontWeight: '700', color: isFailed ? '#fda4af' : '#6ee7b7', textTransform: 'capitalize' }}>
                    {rc.rule?.replace(/_/g, ' ')}
                  </span>
                </div>
                <span className={`badge ${isFailed ? 'badge-fail' : 'badge-pass'}`}>
                  {rc.status}
                </span>
              </div>
              <p style={{ fontSize: '0.8rem', color: '#cbd5e1', marginLeft: '1.5rem' }}>
                {rc.evidence}
              </p>
              {isFailed && rc.recommendation && (
                <div style={{ marginLeft: '1.5rem', fontSize: '0.75rem', color: '#f59e0b', background: 'rgba(245, 158, 11, 0.1)', padding: '0.35rem 0.5rem', borderRadius: '0.25rem' }}>
                  💡 <strong>Recommendation:</strong> {rc.recommendation}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
