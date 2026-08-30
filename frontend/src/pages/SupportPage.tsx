import React from 'react';
import { HelpCircle, Terminal, ShieldCheck } from 'lucide-react';
import { GlassPanel, GlassDeep } from '../components/common/GlassWrappers';
import { useDocumentTitle } from '../hooks/useDocumentTitle';

export const SupportPage: React.FC = () => {
  useDocumentTitle('CCNA Command Cheatsheet & Docs');
  const guideCommands = [
    { cmd: 'show ip interface brief', desc: 'Display summary of interface IP and line protocol statuses' },
    { cmd: 'show ip route', desc: 'Examine IPv4 routing table, static routes, and gateway of last resort' },
    { cmd: 'show interfaces trunk', desc: 'Inspect 802.1Q trunking, Native VLAN configuration, and active VLANs' },
    { cmd: 'show vlan brief', desc: 'Verify VLAN database entries and access port associations' },
    { cmd: 'show ip ospf neighbor', desc: 'Verify dynamic routing adjacencies, state machine (FULL), and router IDs' },
    { cmd: 'show access-lists', desc: 'Inspect numbered/named ACL rules, permit/deny filters, and hit counters' },
  ];

  return (
    <div className="space-y-6 pb-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight flex items-center gap-2.5">
          <HelpCircle className="w-7 h-7 text-primary-container" />
          Documentation &amp; Cisco CCNA Lab Cheatsheet
        </h1>
        <p className="text-xs sm:text-sm text-on-surface-variant mt-1">
          Reference diagnostic commands, safety protocols, and NetSage AI operating rules.
        </p>
      </div>

      {/* Guide Cards */}
      <GlassDeep className="p-5 border border-white/10 space-y-4">
        <div className="flex items-center gap-2 border-b border-white/10 pb-3">
          <Terminal className="w-5 h-5 text-primary-container" />
          <h2 className="text-sm font-bold text-white">Essential Cisco IOS Diagnostic Commands</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {guideCommands.map((item, idx) => (
            <div key={idx} className="glass-card p-3.5 rounded-lg border border-white/5 space-y-1">
              <code className="font-mono text-xs font-bold text-emerald-300 block">{item.cmd}</code>
              <p className="text-xs text-on-surface-variant">{item.desc}</p>
            </div>
          ))}
        </div>
      </GlassDeep>

      {/* Safety Protocol Reminder */}
      <GlassPanel className="p-5 border border-primary-container/30 bg-primary-container/5 space-y-2">
        <div className="flex items-center gap-2 text-primary">
          <ShieldCheck className="w-5 h-5 text-primary-container" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-white">
            Human Verification Protocol
          </h3>
        </div>
        <p className="text-xs text-on-surface-variant leading-relaxed">
          Always review generated commands before committing them to live switches and routers. NetSage AI operates with deterministic rule safeguards and complete explainability.
        </p>
      </GlassPanel>
    </div>
  );
};
