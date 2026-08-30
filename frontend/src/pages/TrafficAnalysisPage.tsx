import React from 'react';
import { Activity, ArrowDownRight, ArrowUpRight, ShieldAlert } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { GlassPanel, GlassCard } from '../components/common/GlassWrappers';
import { StatusBadge } from '../components/common/StatusBadge';
import { useDocumentTitle } from '../hooks/useDocumentTitle';

export const TrafficAnalysisPage: React.FC = () => {
  useDocumentTitle('Traffic Flow & Packet Analysis');
  const throughputData = [
    { time: '10:00', ingress: 45, egress: 42 },
    { time: '10:05', ingress: 52, egress: 48 },
    { time: '10:10', ingress: 58, egress: 55 },
    { time: '10:14', ingress: 12, egress: 4 }, // drop due to admin down
    { time: '10:20', ingress: 14, egress: 5 },
    { time: '10:25', ingress: 62, egress: 60 }, // restored
    { time: '10:30', ingress: 70, egress: 68 },
  ];

  return (
    <div className="space-y-6 pb-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <Activity className="w-7 h-7 text-primary-container" />
            Traffic Flow &amp; Packet Inspection
          </h1>
          <p className="text-xs sm:text-sm text-on-surface-variant mt-1">
            Real-time interface packet counters, ingress/egress bandwidth, and ACL drop telemetry.
          </p>
        </div>
      </div>

      {/* Traffic KPI Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <GlassCard className="p-4 border border-white/10 space-y-2">
          <div className="flex items-center justify-between">
            <span className="label-caps text-outline">Ingress Peak Bandwidth</span>
            <ArrowDownRight className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-white font-mono">70.4 <span className="text-xs text-outline">Mbps</span></div>
          <span className="text-[11px] text-emerald-400 font-mono">Normal Gigabit flow</span>
        </GlassCard>

        <GlassCard className="p-4 border border-white/10 space-y-2">
          <div className="flex items-center justify-between">
            <span className="label-caps text-outline">Egress Output Rate</span>
            <ArrowUpRight className="w-4 h-4 text-secondary" />
          </div>
          <div className="text-2xl font-bold text-secondary font-mono">68.1 <span className="text-xs text-outline">Mbps</span></div>
          <span className="text-[11px] text-outline font-mono">Core Uplink Gi0/0</span>
        </GlassCard>

        <GlassCard className="p-4 border border-white/10 space-y-2">
          <div className="flex items-center justify-between">
            <span className="label-caps text-outline">ACL &amp; Interface Drops</span>
            <ShieldAlert className="w-4 h-4 text-orange-400" />
          </div>
          <div className="text-2xl font-bold text-primary font-mono">128 <span className="text-xs text-outline">pkts</span></div>
          <span className="text-[11px] text-primary font-mono">Captured by ACL 101 rule 20</span>
        </GlassCard>
      </div>

      {/* Throughput chart */}
      <GlassPanel className="p-5 border border-white/10 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-sm font-bold text-white">Interface Gi0/1 Bandwidth (Mbps)</h2>
            <span className="text-[11px] font-mono text-outline">Telemetry showing outage drop and circuit restoration</span>
          </div>
          <StatusBadge status="PASS" size="sm" />
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={throughputData}>
              <defs>
                <linearGradient id="ingressGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ff7a33" stopOpacity={0.6}/>
                  <stop offset="95%" stopColor="#ff7a33" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="egressGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#a5e7ff" stopOpacity={0.6}/>
                  <stop offset="95%" stopColor="#a5e7ff" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <XAxis dataKey="time" stroke="#8e9099" fontSize={11} />
              <YAxis stroke="#8e9099" fontSize={11} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(17, 19, 23, 0.95)',
                  borderColor: 'rgba(255, 255, 255, 0.1)',
                  borderRadius: '8px',
                  fontSize: '12px'
                }}
              />
              <Area type="monotone" dataKey="ingress" stroke="#ff7a33" fillOpacity={1} fill="url(#ingressGrad)" />
              <Area type="monotone" dataKey="egress" stroke="#a5e7ff" fillOpacity={1} fill="url(#egressGrad)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </GlassPanel>
    </div>
  );
};
