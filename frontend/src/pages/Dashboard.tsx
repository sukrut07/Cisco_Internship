import React, { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import {
  FolderGit2,
  CheckCircle2,
  ShieldCheck,
  Zap,
  TrendingUp,
  ArrowUpRight,
  Activity,
  Cpu
} from 'lucide-react';
import { useCase } from '../context/CaseContext';
import { GlassPanel, GlassCard, GlassDeep } from '../components/common/GlassWrappers';
import { StatusBadge } from '../components/common/StatusBadge';
import { SkeletonLoader } from '../components/common/SkeletonLoader';
import { useDocumentTitle } from '../hooks/useDocumentTitle';
import { Case } from '../types';

export const Dashboard: React.FC = () => {
  useDocumentTitle('Operations Dashboard');
  const { cases, loading, setSelectedCaseId } = useCase();
  const navigate = useNavigate();

  // Dynamic live metric calculations
  const metrics = useMemo(() => {
    const total = cases.length;
    if (total === 0) return { total: 0, resolvedPct: 0, agreementPct: 0, correctionPct: 0 };

    const resolved = cases.filter((c: Case) => c.status === 'RESOLVED').length;
    const agreement = cases.filter((c: Case) => c.fusion_status === 'AGREEMENT').length;
    const editedOrRejected = cases.filter((c: Case) => c.status === 'EDITED' || c.status === 'REJECTED').length;

    return {
      total,
      resolvedPct: Math.round((resolved / total) * 100),
      agreementPct: Math.round((agreement / total) * 100),
      correctionPct: Math.round((editedOrRejected / total) * 100)
    };
  }, [cases]);

  // Issue Type / Category chart data computed live
  const categoryData = useMemo(() => {
    const counts: Record<string, number> = {};
    cases.forEach((c: Case) => {
      const cat = c.category.replace(/_/g, ' ');
      counts[cat] = (counts[cat] || 0) + 1;
    });
    return Object.entries(counts).map(([name, count]) => ({
      name,
      count
    }));
  }, [cases]);

  // Severity chart data computed live
  const severityData = useMemo(() => {
    const counts: Record<string, number> = { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0 };
    cases.forEach((c: Case) => {
      if (counts[c.severity] !== undefined) {
        counts[c.severity] += 1;
      }
    });
    return [
      { name: 'CRITICAL', value: counts.CRITICAL, color: '#ff7a33' },
      { name: 'HIGH', value: counts.HIGH, color: '#f87171' },
      { name: 'MEDIUM', value: counts.MEDIUM, color: '#fbbf24' },
      { name: 'LOW', value: counts.LOW, color: '#94a3b8' }
    ].filter(item => item.value > 0);
  }, [cases]);

  // OSI Layer chart data computed live
  const layerData = useMemo(() => {
    const counts: Record<string, number> = {};
    cases.forEach((c: Case) => {
      const layer = c.osi_layer.split('-')[0].trim();
      counts[layer] = (counts[layer] || 0) + 1;
    });
    return Object.entries(counts).map(([name, count]) => ({
      name,
      count
    }));
  }, [cases]);

  const handleOpenCase = (id: string) => {
    setSelectedCaseId(id);
    navigate('/workbench');
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <SkeletonLoader className="h-28 rounded-xl" count={4} />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <SkeletonLoader className="h-80 rounded-xl" count={2} />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-8">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <Activity className="w-7 h-7 text-primary-container" />
            Operations Overview &amp; Intelligence
          </h1>
          <p className="text-xs sm:text-sm text-on-surface-variant mt-1">
            Real-time Cisco Lab Telemetry, AI Root-Cause Convergence &amp; Deterministic Rule Verification
          </p>
        </div>

        <button
          onClick={() => {
            setSelectedCaseId('CASE-004');
            navigate('/workbench');
          }}
          className="px-4 py-2 rounded-lg text-xs font-bold font-sans bg-gradient-to-r from-primary-container to-orange-600 text-white shadow-glow-critical hover:brightness-110 flex items-center gap-2 transition-all active:scale-95 shrink-0"
        >
          <Cpu className="w-4 h-4" />
          <span>Launch AI Workbench</span>
          <ArrowUpRight className="w-4 h-4" />
        </button>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Cases */}
        <GlassCard className="p-4 border border-white/10 relative overflow-hidden flex flex-col justify-between hover:border-primary-container/40">
          <div className="flex items-center justify-between">
            <span className="label-caps text-outline">Total Active Cases</span>
            <div className="w-8 h-8 rounded-lg bg-primary-container/20 flex items-center justify-center">
              <FolderGit2 className="w-4 h-4 text-primary" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="data-mono-bold text-3xl text-white font-bold">{metrics.total}</span>
            <span className="text-xs text-on-surface-variant font-mono">telemetry streams</span>
          </div>
          <div className="mt-2 text-[11px] text-outline flex items-center gap-1">
            <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
            <span>Dataset dynamically synced</span>
          </div>
        </GlassCard>

        {/* AI-Human Agreement */}
        <GlassCard className="p-4 border border-white/10 relative overflow-hidden flex flex-col justify-between hover:border-secondary/40">
          <div className="flex items-center justify-between">
            <span className="label-caps text-outline">AI-Rule Convergence</span>
            <div className="w-8 h-8 rounded-lg bg-secondary/20 flex items-center justify-center">
              <Zap className="w-4 h-4 text-secondary" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="data-mono-bold text-3xl text-secondary font-bold">{metrics.agreementPct}%</span>
            <span className="text-xs text-on-surface-variant font-mono">agreement rate</span>
          </div>
          <div className="mt-2 text-[11px] text-outline">
            <span>Dual-engine consensus metric</span>
          </div>
        </GlassCard>

        {/* Human Correction Rate */}
        <GlassCard className="p-4 border border-white/10 relative overflow-hidden flex flex-col justify-between hover:border-amber-500/40">
          <div className="flex items-center justify-between">
            <span className="label-caps text-outline">Human Intervention</span>
            <div className="w-8 h-8 rounded-lg bg-amber-500/20 flex items-center justify-center">
              <ShieldCheck className="w-4 h-4 text-amber-400" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="data-mono-bold text-3xl text-amber-400 font-bold">{metrics.correctionPct}%</span>
            <span className="text-xs text-on-surface-variant font-mono">override rate</span>
          </div>
          <div className="mt-2 text-[11px] text-outline">
            <span>Mandatory human-in-the-loop</span>
          </div>
        </GlassCard>

        {/* Resolved Rate */}
        <GlassCard className="p-4 border border-white/10 relative overflow-hidden flex flex-col justify-between hover:border-emerald-500/40">
          <div className="flex items-center justify-between">
            <span className="label-caps text-outline">Resolution Success</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-500/20 flex items-center justify-center">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="data-mono-bold text-3xl text-emerald-400 font-bold">{metrics.resolvedPct}%</span>
            <span className="text-xs text-on-surface-variant font-mono">verified resolved</span>
          </div>
          <div className="mt-2 text-[11px] text-outline">
            <span>End-to-end validated</span>
          </div>
        </GlassCard>
      </div>

      {/* Real Dynamic Recharts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Category Breakdown (8 Cols) */}
        <GlassPanel className="lg:col-span-8 p-5 border border-white/10 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-bold text-white tracking-wide">
                Issue Category Distribution
              </h2>
              <span className="text-[11px] font-mono text-outline">
                Computed live from {cases.length} mock test cases
              </span>
            </div>
            <span className="label-caps text-secondary bg-secondary/10 px-2 py-0.5 rounded border border-secondary/30">
              Live Dataset
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryData} margin={{ top: 10, right: 10, left: -15, bottom: 20 }}>
                <XAxis
                  dataKey="name"
                  stroke="#8e9099"
                  fontSize={11}
                  tickLine={false}
                  angle={-15}
                  textAnchor="end"
                />
                <YAxis stroke="#8e9099" fontSize={11} tickLine={false} allowDecimals={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(17, 19, 23, 0.95)',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderRadius: '8px',
                    fontSize: '12px',
                    color: '#fff'
                  }}
                  cursor={{ fill: 'rgba(255, 122, 51, 0.08)' }}
                />
                <Bar dataKey="count" fill="#ff7a33" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </GlassPanel>

        {/* Severity Breakdown Pie Chart (4 Cols) */}
        <GlassPanel className="lg:col-span-4 p-5 border border-white/10 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-2">
            <div>
              <h2 className="text-sm font-bold text-white tracking-wide">
                Severity Breakdown
              </h2>
              <span className="text-[11px] font-mono text-outline">
                By criticality tier
              </span>
            </div>
          </div>

          <div className="h-48 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={severityData}
                  cx="50%"
                  cy="50%"
                  innerRadius={45}
                  outerRadius={70}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {severityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(17, 19, 23, 0.95)',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderRadius: '8px',
                    fontSize: '12px',
                    color: '#fff'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Legend */}
          <div className="grid grid-cols-2 gap-2 pt-2 border-t border-white/10">
            {severityData.map(item => (
              <div key={item.name} className="flex items-center gap-2 text-xs font-mono">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }} />
                <span className="text-on-surface-variant">{item.name}:</span>
                <strong className="text-white">{item.value}</strong>
              </div>
            ))}
          </div>
        </GlassPanel>
      </div>

      {/* Recent Cases Quick Table */}
      <GlassDeep className="p-5 border border-white/10 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FolderGit2 className="w-5 h-5 text-primary-container" />
            <div>
              <h2 className="text-sm font-bold text-white tracking-wide">
                Live Case Telemetry Stream
              </h2>
              <span className="text-[11px] font-mono text-outline">
                Quick diagnostic access
              </span>
            </div>
          </div>

          <button
            onClick={() => navigate('/cases')}
            className="text-xs font-mono text-primary hover:text-primary-container flex items-center gap-1"
          >
            <span>View All Cases &rarr;</span>
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-white/10 text-outline">
                <th className="pb-2.5 font-semibold">CASE ID</th>
                <th className="pb-2.5 font-semibold">TITLE</th>
                <th className="pb-2.5 font-semibold">OSI LAYER</th>
                <th className="pb-2.5 font-semibold">CONCEPT</th>
                <th className="pb-2.5 font-semibold">SEVERITY</th>
                <th className="pb-2.5 font-semibold">FUSION</th>
                <th className="pb-2.5 font-semibold">STATUS</th>
                <th className="pb-2.5 font-semibold text-right">ACTION</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {cases.slice(0, 5).map((c: Case) => (
                <tr key={c.case_id} className="hover:bg-white/[0.03] transition-colors group">
                  <td className="py-3 font-bold text-primary-container">{c.case_id}</td>
                  <td className="py-3 text-white font-sans font-medium">{c.title}</td>
                  <td className="py-3">
                    <span className="text-secondary bg-secondary/10 px-2 py-0.5 rounded border border-secondary/30">
                      {c.osi_layer}
                    </span>
                  </td>
                  <td className="py-3 text-on-surface-variant font-sans">{c.concept}</td>
                  <td className="py-3">
                    <StatusBadge status={c.severity} size="sm" />
                  </td>
                  <td className="py-3">
                    <span
                      className={`text-[10px] font-bold px-1.5 py-0.5 rounded border ${
                        c.fusion_status === 'CONFLICT'
                          ? 'bg-orange-950/40 text-primary border-orange-500/40'
                          : 'bg-emerald-950/40 text-emerald-300 border-emerald-500/30'
                      }`}
                    >
                      {c.fusion_status}
                    </span>
                  </td>
                  <td className="py-3">
                    <StatusBadge status={c.status} size="sm" />
                  </td>
                  <td className="py-3 text-right">
                    <button
                      onClick={() => handleOpenCase(c.case_id)}
                      className="px-2.5 py-1 rounded bg-surface-container hover:bg-primary-container hover:text-white text-on-surface-variant border border-white/10 transition-colors"
                    >
                      Inspect &rarr;
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </GlassDeep>
    </div>
  );
};
