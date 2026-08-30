import React, { useState, useEffect, useRef, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  FolderGit2,
  LayoutDashboard,
  Cpu,
  GitGraph,
  Activity,
  History,
  ShieldCheck,
  HeartPulse,
  HelpCircle,
  RotateCcw,
  Download,
  Terminal,
  LucideIcon
} from 'lucide-react';
import { useCase } from '../../context/CaseContext';
import { Case } from '../../types';

export interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

export interface CommandItem {
  id: string;
  title: string;
  subtitle?: string;
  category: string;
  icon: LucideIcon;
  action?: () => void | Promise<void>;
  path?: string;
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({ isOpen, onClose }) => {
  const { cases, setSelectedCaseId, resetDemoMode } = useCase();
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 50);
      setQuery('');
      setSelectedIndex(0);
    }
  }, [isOpen]);

  const navPages: CommandItem[] = useMemo(() => [
    { id: 'p-dash', title: 'Dashboard', category: 'Navigation', icon: LayoutDashboard, path: '/' },
    { id: 'p-wb', title: 'AI Workbench (CASE-004)', category: 'Navigation', icon: Cpu, path: '/workbench' },
    { id: 'p-cases', title: 'Case Explorer (35 Incidents)', category: 'Navigation', icon: FolderGit2, path: '/cases' },
    { id: 'p-top', title: 'Network Topology Graph', category: 'Navigation', icon: GitGraph, path: '/topology' },
    { id: 'p-traf', title: 'Traffic Flow & Packet Inspection', category: 'Navigation', icon: Activity, path: '/traffic' },
    { id: 'p-audit', title: 'Audit & Compliance Trail', category: 'Navigation', icon: History, path: '/audit' },
    { id: 'p-rai', title: 'Responsible AI Mismatches', category: 'Navigation', icon: ShieldCheck, path: '/responsible-ai' },
    { id: 'p-hlth', title: 'System Health & Latency', category: 'Navigation', icon: HeartPulse, path: '/health' },
    { id: 'p-docs', title: 'CCNA Command Cheatsheet & Docs', category: 'Navigation', icon: HelpCircle, path: '/support' },
  ], []);

  const actions: CommandItem[] = useMemo(() => [
    {
      id: 'act-reset',
      title: 'Reset Demo State to Baseline',
      category: 'Action',
      icon: RotateCcw,
      action: async () => {
        await resetDemoMode();
        onClose();
      }
    },
    {
      id: 'act-export',
      title: 'Export All Cases to CSV (cases.csv)',
      category: 'Action',
      icon: Download,
      action: () => {
        navigate('/cases');
        onClose();
      }
    }
  ], [resetDemoMode, navigate, onClose]);

  const filteredItems: CommandItem[] = useMemo(() => {
    const q = query.toLowerCase().trim();
    if (!q) {
      const initialCaseItems: CommandItem[] = cases.slice(0, 6).map((c: Case) => ({
        id: c.case_id,
        title: `${c.case_id}: ${c.title}`,
        subtitle: `${c.osi_layer} • ${c.concept} • ${c.severity}`,
        category: 'Cases',
        icon: Terminal,
        action: () => {
          setSelectedCaseId(c.case_id);
          navigate('/workbench');
          onClose();
        }
      }));
      return [...actions, ...navPages, ...initialCaseItems];
    }

    const matchedPages = navPages.filter(p => p.title.toLowerCase().includes(q));
    const matchedActions = actions.filter(a => a.title.toLowerCase().includes(q));
    const matchedCases: CommandItem[] = cases
      .filter((c: Case) =>
        c.case_id.toLowerCase().includes(q) ||
        c.title.toLowerCase().includes(q) ||
        c.concept.toLowerCase().includes(q) ||
        c.osi_layer.toLowerCase().includes(q) ||
        c.category.toLowerCase().includes(q)
      )
      .slice(0, 8)
      .map((c: Case) => ({
        id: c.case_id,
        title: `${c.case_id}: ${c.title}`,
        subtitle: `${c.osi_layer} • ${c.concept} • ${c.severity}`,
        category: 'Cases',
        icon: Terminal,
        action: () => {
          setSelectedCaseId(c.case_id);
          navigate('/workbench');
          onClose();
        }
      }));

    return [...matchedActions, ...matchedPages, ...matchedCases];
  }, [query, cases, navPages, actions, navigate, setSelectedCaseId, onClose]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(prev => (prev + 1) % Math.max(1, filteredItems.length));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(prev => (prev - 1 + filteredItems.length) % Math.max(1, filteredItems.length));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      const item = filteredItems[selectedIndex];
      if (item) {
        if (item.action && typeof item.action === 'function') {
          item.action();
        } else if (item.path) {
          navigate(item.path);
          onClose();
        }
      }
    } else if (e.key === 'Escape') {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4 bg-black/70 backdrop-blur-md animate-fadeIn"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label="Command Palette"
    >
      <div
        className="glass-panel w-full max-w-2xl rounded-2xl border border-white/20 shadow-2xl overflow-hidden flex flex-col bg-[#111317]/95"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Input Bar */}
        <div className="flex items-center px-4 py-3.5 border-b border-white/10 gap-3">
          <Search className="w-5 h-5 text-primary-container shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            onKeyDown={handleKeyDown}
            placeholder="Type a command, route, or search 35 Cisco incidents..."
            className="w-full bg-transparent text-sm text-white placeholder:text-outline focus:outline-none font-sans"
            aria-label="Command search query"
          />
          <kbd className="px-2 py-0.5 text-[10px] font-mono text-outline bg-white/5 border border-white/10 rounded">
            ESC
          </kbd>
        </div>

        {/* Results List */}
        <div className="max-h-96 overflow-y-auto p-2 space-y-1">
          {filteredItems.length === 0 ? (
            <div className="p-8 text-center text-outline text-xs">
              No matching commands or cases found.
            </div>
          ) : (
            filteredItems.map((item, idx) => {
              const isSelected = idx === selectedIndex;
              const Icon = item.icon;

              return (
                <div
                  key={item.id}
                  onClick={() => {
                    if (item.action && typeof item.action === 'function') {
                      item.action();
                    } else if (item.path) {
                      navigate(item.path);
                      onClose();
                    }
                  }}
                  onMouseEnter={() => setSelectedIndex(idx)}
                  className={`p-3 rounded-xl flex items-center justify-between gap-3 cursor-pointer transition-colors ${
                    isSelected
                      ? 'bg-primary-container/20 border border-primary-container/40 text-white'
                      : 'text-on-surface hover:bg-white/[0.04] border border-transparent'
                  }`}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div
                      className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                        isSelected ? 'bg-primary-container text-white' : 'bg-surface-container text-outline'
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                    </div>
                    <div className="min-w-0">
                      <div className="font-semibold text-xs text-white truncate">
                        {item.title}
                      </div>
                      {item.subtitle && (
                        <div className="text-[11px] text-on-surface-variant font-mono truncate">
                          {item.subtitle}
                        </div>
                      )}
                    </div>
                  </div>

                  <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-surface-container text-outline border border-white/5 shrink-0">
                    {item.category}
                  </span>
                </div>
              );
            })
          )}
        </div>

        {/* Footer shortcuts */}
        <div className="px-4 py-2.5 bg-black/40 border-t border-white/10 flex items-center justify-between text-[11px] font-mono text-outline select-none">
          <div className="flex items-center gap-3">
            <span><kbd className="text-white">↑↓</kbd> Navigate</span>
            <span><kbd className="text-white">↵</kbd> Select</span>
            <span><kbd className="text-white">ESC</kbd> Close</span>
          </div>
          <span>NetSage Fast Navigation</span>
        </div>
      </div>
    </div>
  );
};
