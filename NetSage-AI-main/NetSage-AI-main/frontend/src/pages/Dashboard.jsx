import React, { useEffect, useState } from 'react';
import { 
  Activity, 
  CheckCircle, 
  Edit3, 
  XCircle, 
  Percent, 
  ShieldCheck, 
  AlertOctagon, 
  Layers,
  ArrowRight,
  RefreshCw
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Legend 
} from 'recharts';
import MetricCard from '../components/MetricCard';
import { getDashboardStats } from '../services/api';

const COLORS = ['#06b6d4', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#f43f5e', '#14b8a6'];

export default function Dashboard({ setActivePage, setSelectedCaseId }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const data = await getDashboardStats();
      setStats(data);
    } catch (err) {
      console.error('Failed to fetch dashboard stats', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <RefreshCw className="animate-spin" size={32} color="#06b6d4" />
        <span style={{ marginLeft: '0.75rem', color: '#94a3b8' }}>Loading NetSage Telemetry Dashboard...</span>
      </div>
    );
  }

  // Format Recharts data
  const conceptData = Object.entries(stats?.by_concept || {}).map(([name, value]) => ({ name, value }));
  const severityData = Object.entries(stats?.by_severity || {}).map(([name, value]) => ({ name, value }));
  const osiData = Object.entries(stats?.by_osi_layer || {}).map(([name, value]) => ({ name, value }));
  
  const reviewData = [
    { name: 'Accepted', value: stats?.accepted_diagnoses || 0, color: '#10b981' },
    { name: 'Edited', value: stats?.edited_diagnoses || 0, color: '#f59e0b' },
    { name: 'Rejected', value: stats?.rejected_diagnoses || 0, color: '#f43f5e' }
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* Dashboard Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: '700', color: '#f8fafc' }}>
            Troubleshooting Analytics Dashboard
          </h2>
          <p style={{ fontSize: '0.875rem', color: '#94a3b8' }}>
            Real-time Cisco lab diagnostic metrics, human review decisions, and AI reliability telemetry.
          </p>
        </div>
        <button className="btn btn-primary" onClick={() => setActivePage('new-case')}>
          + New Troubleshooting Case
        </button>
      </div>

      {/* Metric Cards Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))', gap: '1rem' }}>
        <MetricCard 
          title="Total Cases" 
          value={stats?.total_cases || 0} 
          subtitle="Analyzed labs & scenarios" 
          icon={Activity} 
          color="#06b6d4" 
        />
        <MetricCard 
          title="Accepted Diagnoses" 
          value={stats?.accepted_diagnoses || 0} 
          subtitle="Human approved AI output" 
          icon={CheckCircle} 
          color="#10b981" 
        />
        <MetricCard 
          title="Edited Diagnoses" 
          value={stats?.edited_diagnoses || 0} 
          subtitle="Human corrected details" 
          icon={Edit3} 
          color="#f59e0b" 
        />
        <MetricCard 
          title="Rejected Diagnoses" 
          value={stats?.rejected_diagnoses || 0} 
          subtitle="Human rejected AI diagnosis" 
          icon={XCircle} 
          color="#f43f5e" 
        />
        <MetricCard 
          title="Agreement Rate" 
          value={`${stats?.agreement_rate || 0}%`} 
          subtitle="Accepted / Reviewed cases" 
          icon={Percent} 
          color="#3b82f6" 
        />
        <MetricCard 
          title="AI Correction Count" 
          value={stats?.correction_count || 0} 
          subtitle="Edited + Rejected count" 
          icon={ShieldCheck} 
          color="#8b5cf6" 
        />
      </div>

      {/* Visual Analytics Charts Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1.25rem' }}>
        
        {/* Cases by Concept (Pie Chart) */}
        <div className="glass-card">
          <h3 style={{ fontSize: '1rem', fontWeight: '700', color: '#f1f5f9', marginBottom: '1rem' }}>
            Cases by Networking Concept
          </h3>
          <div style={{ width: '100%', height: 260 }}>
            <ResponsiveContainer>
              <PieChart>
                <Pie 
                  data={conceptData} 
                  dataKey="value" 
                  nameKey="name" 
                  cx="50%" 
                  cy="50%" 
                  outerRadius={90} 
                  label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                >
                  {conceptData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: '#0f172a', borderColor: '#334155', color: '#fff' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Human Decisions (Donut Chart) */}
        <div className="glass-card">
          <h3 style={{ fontSize: '1rem', fontWeight: '700', color: '#f1f5f9', marginBottom: '1rem' }}>
            Human Decision Breakdown
          </h3>
          <div style={{ width: '100%', height: 260 }}>
            <ResponsiveContainer>
              <PieChart>
                <Pie 
                  data={reviewData} 
                  dataKey="value" 
                  nameKey="name" 
                  cx="50%" 
                  cy="50%" 
                  innerRadius={50} 
                  outerRadius={85} 
                  paddingAngle={5}
                >
                  {reviewData.map((entry, index) => (
                    <Cell key={`cell-review-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: '#0f172a', borderColor: '#334155', color: '#fff' }} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Cases by Severity (Bar Chart) */}
        <div className="glass-card">
          <h3 style={{ fontSize: '1rem', fontWeight: '700', color: '#f1f5f9', marginBottom: '1rem' }}>
            Cases by Fault Severity
          </h3>
          <div style={{ width: '100%', height: 260 }}>
            <ResponsiveContainer>
              <BarChart data={severityData}>
                <XAxis dataKey="name" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" allowDecimals={false} />
                <Tooltip contentStyle={{ background: '#0f172a', borderColor: '#334155', color: '#fff' }} />
                <Bar dataKey="value" fill="#06b6d4" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Cases by OSI Layer (Bar Chart) */}
        <div className="glass-card">
          <h3 style={{ fontSize: '1rem', fontWeight: '700', color: '#f1f5f9', marginBottom: '1rem' }}>
            Distribution by OSI Layer
          </h3>
          <div style={{ width: '100%', height: 260 }}>
            <ResponsiveContainer>
              <BarChart data={osiData} layout="vertical">
                <XAxis type="number" stroke="#94a3b8" allowDecimals={false} />
                <YAxis dataKey="name" type="category" stroke="#94a3b8" width={140} style={{ fontSize: '0.75rem' }} />
                <Tooltip contentStyle={{ background: '#0f172a', borderColor: '#334155', color: '#fff' }} />
                <Bar dataKey="value" fill="#3b82f6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

      {/* Recent Cases Table */}
      <div className="glass-card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: '700', color: '#f1f5f9' }}>
            Recent Troubleshooting Cases
          </h3>
          <button 
            className="btn btn-secondary" 
            onClick={() => setActivePage('cases')}
            style={{ fontSize: '0.8rem', padding: '0.35rem 0.75rem' }}
          >
            <span>View All Directory</span>
            <ArrowRight size={14} />
          </button>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #1e293b', color: '#64748b' }}>
                <th style={{ padding: '0.75rem' }}>Case ID</th>
                <th style={{ padding: '0.75rem' }}>Title</th>
                <th style={{ padding: '0.75rem' }}>Concept</th>
                <th style={{ padding: '0.75rem' }}>Severity</th>
                <th style={{ padding: '0.75rem' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {stats?.recent_cases?.map((c) => (
                <tr key={c.id} style={{ borderBottom: '1px solid #131b2e' }}>
                  <td style={{ padding: '0.75rem', fontFamily: 'Fira Code', fontWeight: '600', color: '#06b6d4' }}>
                    {c.id}
                  </td>
                  <td style={{ padding: '0.75rem', fontWeight: '600', color: '#f1f5f9' }}>
                    {c.title}
                  </td>
                  <td style={{ padding: '0.75rem' }}>
                    <span className="badge badge-info">{c.concept}</span>
                  </td>
                  <td style={{ padding: '0.75rem' }}>
                    <span className={`badge ${c.severity === 'Critical' ? 'badge-fail' : c.severity === 'High' ? 'badge-warning' : 'badge-info'}`}>
                      {c.severity}
                    </span>
                  </td>
                  <td style={{ padding: '0.75rem' }}>
                    <button
                      className="btn btn-secondary"
                      onClick={() => {
                        setSelectedCaseId(c.id);
                        setActivePage('case-detail');
                      }}
                      style={{ padding: '0.25rem 0.6rem', fontSize: '0.75rem' }}
                    >
                      Diagnose & Review
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
