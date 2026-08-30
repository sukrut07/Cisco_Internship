import React, { useState } from 'react';
import { GitGraph, Server, Laptop, Router, Network } from 'lucide-react';
import { useCase } from '../context/CaseContext';
import { GlassPanel, GlassCard, GlassDeep } from '../components/common/GlassWrappers';
import { StatusBadge } from '../components/common/StatusBadge';
import { useDocumentTitle } from '../hooks/useDocumentTitle';

export const NetworkMapPage: React.FC = () => {
  useDocumentTitle('Network Topology Map');
  const { currentCase, setSelectedCaseId } = useCase();
  const [selectedNode, setSelectedNode] = useState<string>('R1');

  const nodes = [
    {
      id: 'PC1',
      name: 'PC1 (Client Host)',
      type: 'host',
      ip: '192.168.1.10/24',
      mac: '0019.AA11.2233',
      status: 'UP',
      icon: Laptop
    },
    {
      id: 'SW1',
      name: 'SW1 (Access Switch)',
      type: 'switch',
      ip: 'VLAN1: 192.168.1.2',
      status: 'UP',
      icon: Network
    },
    {
      id: 'R1',
      name: 'R1 (Core Gateway)',
      type: 'router',
      ip: 'Gi0/0: 192.168.1.1 | Gi0/1: 10.0.0.1',
      status: currentCase?.case_id === 'CASE-004' && currentCase.status !== 'RESOLVED' ? 'ADMIN_DOWN' : 'UP',
      icon: Router
    },
    {
      id: 'Server1',
      name: 'Server1 (Intranet Host)',
      type: 'server',
      ip: '10.0.0.100/24',
      status: 'UP',
      icon: Server
    }
  ];

  return (
    <div className="space-y-6 pb-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <GitGraph className="w-7 h-7 text-primary-container" />
            Interactive Network Topology
          </h1>
          <p className="text-xs sm:text-sm text-on-surface-variant mt-1">
            Visual Packet Tracer diagram with node telemetry, interface mappings, and live link statuses.
          </p>
        </div>

        <div className="flex items-center gap-2 font-mono text-xs text-outline">
          <span>Active Case Context:</span>
          <span className="font-bold text-primary-container">{currentCase?.case_id || 'CASE-004'}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
        {/* Visual Map (8 Cols) */}
        <div className="xl:col-span-8 space-y-4">
          <GlassDeep className="p-6 border border-white/10 relative min-h-[440px] flex flex-col justify-between overflow-hidden">
            {/* Top Toolbar */}
            <div className="flex items-center justify-between z-10">
              <div className="flex items-center gap-2">
                <span className="label-caps text-secondary bg-secondary/10 px-2 py-0.5 rounded border border-secondary/30">
                  Packet Tracer Lab Topology
                </span>
              </div>
              <span className="text-[11px] font-mono text-outline">
                Click any device node to inspect telemetry
              </span>
            </div>

            {/* Visual Topology Diagram Nodes & Links */}
            <div className="my-8 flex flex-col sm:flex-row items-center justify-around gap-4 relative z-10">
              {nodes.map((node, index) => {
                const Icon = node.icon;
                const isSelected = selectedNode === node.id;
                const isDown = node.status === 'ADMIN_DOWN';

                return (
                  <React.Fragment key={node.id}>
                    {/* Device Node */}
                    <div
                      onClick={() => setSelectedNode(node.id)}
                      className={`p-4 rounded-xl border flex flex-col items-center gap-2 cursor-pointer transition-all ${
                        isSelected
                          ? 'glass-panel border-primary-container scale-105 shadow-glow-critical bg-primary-container/10'
                          : isDown
                          ? 'glass-card border-red-500/50 bg-red-950/20 hover:scale-102'
                          : 'glass-card border-white/10 hover:border-white/20 hover:scale-102'
                      }`}
                    >
                      <div
                        className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                          isDown
                            ? 'bg-red-500/20 text-red-400 border border-red-500/40'
                            : isSelected
                            ? 'bg-primary-container text-white shadow-glow-critical'
                            : 'bg-surface-container text-secondary border border-white/10'
                        }`}
                      >
                        <Icon className="w-6 h-6" />
                      </div>

                      <div className="text-center">
                        <span className="font-mono text-xs font-bold text-white block">
                          {node.name.split(' ')[0]}
                        </span>
                        <span className="text-[10px] text-on-surface-variant font-mono">
                          {node.type.toUpperCase()}
                        </span>
                      </div>

                      <StatusBadge status={isDown ? 'CRITICAL' : 'PASS'} size="sm" />
                    </div>

                    {/* Connecting Link Line */}
                    {index < nodes.length - 1 && (
                      <div className="hidden sm:flex flex-col items-center justify-center flex-1 max-w-[80px]">
                        <div
                          className={`h-1 w-full rounded transition-all ${
                            index === 1 && isDown
                              ? 'bg-red-500/60 shadow-[0_0_8px_#ef4444]'
                              : 'bg-emerald-500/60 shadow-[0_0_8px_#10b981]'
                          }`}
                        />
                        <span className="text-[9px] font-mono text-outline mt-1">
                          {index === 0 ? 'Fa0/1' : index === 1 ? 'Gi0/1' : '10.0.0.x'}
                        </span>
                      </div>
                    )}
                  </React.Fragment>
                );
              })}
            </div>

            {/* Bottom Status bar */}
            <div className="z-10 bg-black/40 p-3 rounded-lg border border-white/5 flex items-center justify-between text-xs font-mono">
              <span className="text-outline">Active Circuit: PC1 &rarr; SW1 &rarr; R1 &rarr; Server1</span>
              <span className="text-emerald-300">Telemetry Sync: 100% GigaBit</span>
            </div>
          </GlassDeep>
        </div>

        {/* Node Telemetry Inspector (4 Cols) */}
        <div className="xl:col-span-4 space-y-4">
          <GlassPanel className="p-5 border border-white/10 space-y-4">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <h3 className="text-sm font-bold text-white tracking-wide">
                Device Telemetry: {selectedNode}
              </h3>
              <StatusBadge
                status={selectedNode === 'R1' && currentCase?.case_id === 'CASE-004' && currentCase.status !== 'RESOLVED' ? 'CRITICAL' : 'PASS'}
                size="sm"
              />
            </div>

            <div className="space-y-3 text-xs font-mono">
              <div>
                <span className="text-outline text-[11px] block">DEVICE NAME</span>
                <span className="text-white font-bold">{nodes.find(n => n.id === selectedNode)?.name}</span>
              </div>
              <div>
                <span className="text-outline text-[11px] block">IP ASSIGNMENTS</span>
                <span className="text-secondary">{nodes.find(n => n.id === selectedNode)?.ip}</span>
              </div>
              <div>
                <span className="text-outline text-[11px] block">OPERATIONAL STATUS</span>
                <span className="text-on-surface">
                  {selectedNode === 'R1' && currentCase?.case_id === 'CASE-004' && currentCase.status !== 'RESOLVED'
                    ? 'Gi0/1 is administratively down (Shutdown flag active)'
                    : 'All interfaces up / protocol operational'}
                </span>
              </div>
            </div>

            <button
              onClick={() => setSelectedCaseId(currentCase?.case_id || 'CASE-004')}
              className="w-full py-2 bg-primary-container/20 hover:bg-primary-container text-primary hover:text-white rounded-lg border border-primary-container/40 text-xs font-mono font-bold transition-all"
            >
              Analyze in AI Workbench &rarr;
            </button>
          </GlassPanel>
        </div>
      </div>
    </div>
  );
};
