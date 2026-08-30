import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Cpu,
  FolderGit2,
  GitGraph,
  Activity,
  History,
  ShieldCheck,
  HeartPulse,
  HelpCircle,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  Zap,
  RotateCcw
} from 'lucide-react';
import { useCase } from '../../context/CaseContext';

export const SideNavBar: React.FC = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const location = useLocation();
  const { resetDemoMode, refreshCases, loading } = useCase();
  const [syncing, setSyncing] = useState(false);

  const handleSync = async () => {
    setSyncing(true);
    await refreshCases(true);
    setTimeout(() => setSyncing(false), 500);
  };

  const navItemsTop = [
    { label: 'Dashboard', path: '/', icon: LayoutDashboard },
    { label: 'AI Workbench', path: '/workbench', icon: Cpu, badge: 'HERO' },
    { label: 'Case Explorer', path: '/cases', icon: FolderGit2 },
    { label: 'Network Topology', path: '/topology', icon: GitGraph },
    { label: 'Traffic Analysis', path: '/traffic', icon: Activity },
    { label: 'Audit Log', path: '/audit', icon: History },
    { label: 'Responsible AI', path: '/responsible-ai', icon: ShieldCheck },
  ];

  const navItemsBottom = [
    { label: 'System Health', path: '/health', icon: HeartPulse },
    { label: 'Support & Docs', path: '/support', icon: HelpCircle },
  ];

  return (
    <aside
      aria-label="Sidebar Navigation"
      className={`fixed top-0 left-0 bottom-0 z-30 flex flex-col justify-between glass-deep border-r border-white/10 transition-all duration-300 ${
        isCollapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Brand Header */}
      <div>
        <div className="h-16 px-4 flex items-center justify-between border-b border-white/10">
          <div className="flex items-center gap-3 overflow-hidden">
            {/* Logo Icon */}
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-primary-container to-orange-600 flex items-center justify-center shadow-glow-critical shrink-0">
              <Zap className="w-5 h-5 text-white" />
            </div>
            {!isCollapsed && (
              <div className="flex flex-col">
                <span className="font-bold text-base tracking-tight text-white font-sans flex items-center gap-1.5">
                  NetSage <span className="text-primary-container">AI</span>
                </span>
                <span className="text-[10px] font-mono text-outline tracking-wider">
                  v2.4-CISCO-LAB
                </span>
              </div>
            )}
          </div>

          {/* Toggle Button */}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1.5 rounded hover:bg-white/10 text-on-surface-variant hover:text-white transition-colors"
            aria-label={isCollapsed ? 'Expand sidebar navigation' : 'Collapse sidebar navigation'}
            title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        {/* Top Navigation Links */}
        <nav aria-label="Main App Sections" className="p-2 space-y-1 mt-2">
          {navItemsTop.map(item => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path || 
              (item.path !== '/' && location.pathname.startsWith(item.path));

            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-all group relative ${
                  isActive
                    ? 'bg-primary-container/15 text-primary border-l-2 border-primary-container shadow-inner'
                    : 'text-on-surface-variant hover:text-white hover:bg-white/[0.04]'
                }`}
                title={isCollapsed ? item.label : undefined}
                aria-label={item.label}
              >
                <Icon
                  className={`w-5 h-5 shrink-0 transition-colors ${
                    isActive ? 'text-primary-container' : 'text-on-surface-variant group-hover:text-white'
                  }`}
                />
                {!isCollapsed && (
                  <span className="truncate flex-1 font-sans">{item.label}</span>
                )}
                {!isCollapsed && item.badge && (
                  <span className="text-[9px] font-mono font-bold bg-primary-container/30 text-primary px-1.5 py-0.5 rounded border border-primary-container/40">
                    {item.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Bottom Section */}
      <div className="p-2 border-t border-white/10 space-y-2">
        <nav aria-label="System Utilities" className="space-y-1">
          {navItemsBottom.map(item => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-3 py-2 rounded-md text-xs font-medium transition-colors ${
                  isActive
                    ? 'bg-white/10 text-white border-l-2 border-secondary'
                    : 'text-on-surface-variant hover:text-white hover:bg-white/[0.04]'
                }`}
                title={isCollapsed ? item.label : undefined}
                aria-label={item.label}
              >
                <Icon className="w-4 h-4 shrink-0" />
                {!isCollapsed && <span className="truncate">{item.label}</span>}
              </NavLink>
            );
          })}
        </nav>

        {/* Demo Mode Reset Button */}
        <button
          onClick={resetDemoMode}
          className={`w-full flex items-center gap-2 px-3 py-2 rounded-md text-xs font-mono font-semibold bg-white/[0.04] hover:bg-white/[0.08] text-amber-300 border border-amber-500/20 transition-all ${
            isCollapsed ? 'justify-center' : 'justify-start'
          }`}
          title="Reset Demo Baseline State"
          aria-label="Reset Demo Baseline State"
        >
          <RotateCcw className="w-3.5 h-3.5 text-amber-400 shrink-0" />
          {!isCollapsed && <span>Reset Demo State</span>}
        </button>

        {/* Force Sync Button */}
        <button
          onClick={handleSync}
          disabled={syncing || loading}
          className={`w-full flex items-center gap-2 px-3 py-2 rounded-md text-xs font-mono text-on-surface-variant hover:text-white bg-surface-container hover:bg-surface-container-high border border-white/10 transition-colors ${
            isCollapsed ? 'justify-center' : 'justify-start'
          }`}
          title="Force Database Sync"
          aria-label="Force Database Sync"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${syncing ? 'animate-spin text-primary-container' : ''}`} />
          {!isCollapsed && <span>{syncing ? 'Syncing...' : 'Force Sync'}</span>}
        </button>
      </div>
    </aside>
  );
};
