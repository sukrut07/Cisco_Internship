import React from 'react';

export default function MetricCard({ title, value, subtitle, icon: Icon, color = '#06b6d4', trend }) {
  return (
    <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span style={{ fontSize: '0.85rem', fontWeight: '600', color: '#94a3b8' }}>{title}</span>
        {Icon && (
          <div style={{ background: `${color}20`, padding: '0.4rem', borderRadius: '0.375rem', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Icon size={18} color={color} />
          </div>
        )}
      </div>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem' }}>
        <span style={{ fontSize: '1.75rem', fontWeight: '700', color: '#f8fafc', letterSpacing: '-0.025em' }}>
          {value}
        </span>
        {trend && (
          <span style={{ fontSize: '0.75rem', fontWeight: '600', color: trend.startsWith('+') ? '#10b981' : '#f43f5e' }}>
            {trend}
          </span>
        )}
      </div>
      {subtitle && (
        <span style={{ fontSize: '0.75rem', color: '#64748b' }}>{subtitle}</span>
      )}
    </div>
  );
}
