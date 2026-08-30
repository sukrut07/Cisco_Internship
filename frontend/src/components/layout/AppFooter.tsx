import React from 'react';
import { ShieldCheck, Terminal, Cpu } from 'lucide-react';

export const AppFooter: React.FC = () => {
  return (
    <footer className="h-10 px-6 glass-deep border-t border-white/10 flex items-center justify-between text-xs text-on-surface-variant select-none">
      {/* Left: Status Pill */}
      <div className="flex items-center gap-4 font-mono text-[11px]">
        <div className="flex items-center gap-2 px-2.5 py-0.5 rounded-full bg-emerald-950/40 border border-emerald-500/30 text-emerald-400">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse-indicator" />
          <span className="font-semibold">SYSTEM OPERATIONAL</span>
        </div>
        <span className="hidden sm:inline text-outline">
          Deterministic Rule Engine: <strong className="text-white">Active</strong> (11 Rules)
        </span>
        <span className="hidden md:inline text-outline">
          AI Guardrail: <strong className="text-secondary">Mandatory Human Stop</strong>
        </span>
      </div>

      {/* Right: Policy & Protocol */}
      <div className="flex items-center gap-4 text-[11px] font-mono">
        <span className="flex items-center gap-1 text-outline hover:text-white transition-colors cursor-pointer">
          <ShieldCheck className="w-3.5 h-3.5 text-primary-container" />
          <span className="hidden sm:inline">Human Gateway Policy v1.2</span>
        </span>
        <span className="text-white/20">|</span>
        <span className="flex items-center gap-1 text-outline hover:text-white transition-colors cursor-pointer">
          <Terminal className="w-3.5 h-3.5 text-secondary" />
          <span className="hidden sm:inline">Packet Tracer Telemetry</span>
        </span>
      </div>
    </footer>
  );
};
