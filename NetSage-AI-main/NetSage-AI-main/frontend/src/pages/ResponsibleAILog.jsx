import React, { useState, useEffect } from 'react';
import { ShieldCheck, AlertTriangle, Percent, CheckCircle2, RefreshCw, UserCheck } from 'lucide-react';
import MetricCard from '../components/MetricCard';
import { getResponsibleAILogs } from '../services/api';

export default function ResponsibleAILog() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const res = await getResponsibleAILogs();
      setData(res);
    } catch (err) {
      console.error('Failed to fetch Responsible AI audit log', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <RefreshCw className="animate-spin" size={32} color="#06b6d4" />
        <span style={{ marginLeft: '0.75rem', color: '#94a3b8' }}>Loading Responsible AI Audit Telemetry...</span>
      </div>
    );
  }

  const metrics = data?.metrics;
  const logs = data?.corrections_log || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* Header */}
      <div>
        <h2 style={{ fontSize: '1.5rem', fontWeight: '700', color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <ShieldCheck size={24} color="#06b6d4" />
          <span>Responsible AI & Human-in-the-Loop Audit Log</span>
        </h2>
        <p style={{ fontSize: '0.875rem', color: '#94a3b8' }}>
          Transparent tracking of human engineer corrections, AI error analysis, and safety compliance metrics.
        </p>
      </div>

      {/* KPI Cards Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
        <MetricCard 
          title="AI-Human Agreement Rate" 
          value={`${metrics?.agreement_rate || 0}%`} 
          subtitle="Accepted AI diagnoses" 
          icon={Percent} 
          color="#10b981" 
        />
        <MetricCard 
          title="AI Correction Rate" 
          value={`${metrics?.correction_rate || 0}%`} 
          subtitle="Edited + Rejected diagnoses" 
          icon={AlertTriangle} 
          color="#f59e0b" 
        />
        <MetricCard 
          title="Total Reviewed Cases" 
          value={metrics?.total_reviews || 0} 
          subtitle="Reviewed by NetEngineers" 
          icon={UserCheck} 
          color="#3b82f6" 
        />
        <MetricCard 
          title="Human Corrections Logged" 
          value={metrics?.correction_count || 0} 
          subtitle="Documented AI adjustments" 
          icon={ShieldCheck} 
          color="#8b5cf6" 
        />
      </div>

      {/* Corrections Log Audit Table */}
      <div className="glass-card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: '700', color: '#f1f5f9' }}>
            Human Correction Cases ({logs.length})
          </h3>
          <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
            Showing AI vs Human Override records
          </span>
        </div>

        {logs.length === 0 ? (
          <div style={{ padding: '2rem', textAlign: 'center', color: '#64748b' }}>
            No human corrections recorded yet.
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #1e293b', color: '#64748b' }}>
                  <th style={{ padding: '0.85rem' }}>Case ID</th>
                  <th style={{ padding: '0.85rem' }}>Decision</th>
                  <th style={{ padding: '0.85rem' }}>Original AI Diagnosis</th>
                  <th style={{ padding: '0.85rem' }}>Human Correction</th>
                  <th style={{ padding: '0.85rem' }}>Reason for Correction</th>
                  <th style={{ padding: '0.85rem' }}>Reviewer & Date</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <tr key={log.id} style={{ borderBottom: '1px solid #131b2e' }}>
                    <td style={{ padding: '0.85rem', fontFamily: 'Fira Code', fontWeight: '700', color: '#06b6d4' }}>
                      {log.case_id}
                    </td>
                    <td style={{ padding: '0.85rem' }}>
                      <span className={`badge ${log.decision === 'EDIT' ? 'badge-warning' : 'badge-fail'}`}>
                        {log.decision}
                      </span>
                    </td>
                    <td style={{ padding: '0.85rem', color: '#fda4af', maxWidth: '220px' }}>
                      {log.original_ai_diagnosis}
                    </td>
                    <td style={{ padding: '0.85rem', color: '#6ee7b7', fontWeight: '600', maxWidth: '240px' }}>
                      {log.human_correction}
                    </td>
                    <td style={{ padding: '0.85rem', color: '#cbd5e1', fontStyle: 'italic', maxWidth: '200px' }}>
                      "{log.reason_for_correction}"
                    </td>
                    <td style={{ padding: '0.85rem', color: '#94a3b8', fontSize: '0.75rem' }}>
                      <div><strong>{log.reviewer}</strong></div>
                      <div>{log.date}</div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

    </div>
  );
}
