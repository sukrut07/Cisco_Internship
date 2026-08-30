import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Folder,
  Search,
  Settings,
  GitFork,
  ArrowRight,
  ShieldAlert,
  CheckCircle2,
  ChevronDown,
  Command
} from 'lucide-react';
import { useCase } from '../../context/CaseContext';
import { CommandPalette } from '../common/CommandPalette';
import { Case } from '../../types';

interface TopAppBarProps {
  caseId?: string;
}

export const TopAppBar: React.FC<TopAppBarProps> = ({ caseId }) => {
  const { cases, currentCase, setSelectedCaseId, selectedCaseId } = useCase();
  const [isCaseDropdownOpen, setIsCaseDropdownOpen] = useState(false);
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  const location = useLocation();

  const activeId = caseId || currentCase?.case_id || selectedCaseId || 'CASE-004';

  // Global keyboard shortcuts: '/' or 'Cmd+K' / 'Ctrl+K'
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setIsCommandPaletteOpen(prev => !prev);
      } else if (e.key === '/' && !isCommandPaletteOpen && document.activeElement?.tagName !== 'INPUT' && document.activeElement?.tagName !== 'TEXTAREA') {
        e.preventDefault();
        setIsCommandPaletteOpen(true);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isCommandPaletteOpen]);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsCaseDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelectCase = (id: string) => {
    setSelectedCaseId(id);
    setIsCaseDropdownOpen(false);
    if (!location.pathname.startsWith('/workbench') && !location.pathname.startsWith('/review') && !location.pathname.startsWith('/verification')) {
      navigate('/workbench');
    }
  };

  const getCtaButton = () => {
    if (!currentCase) return null;

    if (currentCase.status === 'REVIEW_REQUIRED' || currentCase.status === 'DIAGNOSIS_READY') {
      return (
        <button
          onClick={() => navigate('/review')}
          className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-gradient-to-r from-orange-500 to-primary-container text-white shadow-glow-critical hover:brightness-110 active:scale-95 transition-all font-sans"
          aria-label="Proceed to Human Review"
        >
          <ShieldAlert className="w-3.5 h-3.5" />
          <span>Human Review</span>
          <ArrowRight className="w-3 h-3" />
        </button>
      );
    }

    if (currentCase.status === 'ACCEPTED' || currentCase.status === 'EDITED') {
      return (
        <button
          onClick={() => navigate('/review')}
          className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-gradient-to-r from-primary-container to-orange-600 text-white shadow-glow-critical hover:brightness-110 active:scale-95 transition-all font-sans"
          aria-label="Approve Remediation Fix"
        >
          <span>Approve Fix</span>
          <ArrowRight className="w-3 h-3" />
        </button>
      );
    }

    if (currentCase.status === 'FIX_APPROVED' || currentCase.status === 'VERIFICATION') {
      return (
        <button
          onClick={() => navigate('/verification')}
          className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-gradient-to-r from-cyan-500 to-secondary text-slate-950 font-bold shadow-glow-cyan hover:brightness-110 active:scale-95 transition-all font-sans"
          aria-label="Run Live Verification Probes"
        >
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>Verify Live</span>
          <ArrowRight className="w-3 h-3" />
        </button>
      );
    }

    return (
      <button
        onClick={() => navigate('/workbench')}
        className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-white/10 hover:bg-white/15 text-white border border-white/10 transition-all font-sans"
        aria-label="Open AI Workbench"
      >
        <span>AI Workbench</span>
      </button>
    );
  };

  return (
    <>
      <header className="h-16 px-6 glass-deep border-b border-white/10 flex items-center justify-between sticky top-0 z-20" role="banner">
        {/* Left: Breadcrumb & Case Switcher */}
        <div className="flex items-center gap-3 relative" ref={dropdownRef}>
          <div
            onClick={() => setIsCaseDropdownOpen(!isCaseDropdownOpen)}
            className="flex items-center gap-2.5 px-3 py-1.5 rounded-lg bg-surface-container hover:bg-surface-container-high border border-white/10 cursor-pointer transition-colors group select-none"
            role="button"
            tabIndex={0}
            aria-haspopup="true"
            aria-expanded={isCaseDropdownOpen}
            aria-label={`Current case ${activeId}. Click to switch case.`}
          >
            <Folder className="w-4 h-4 text-primary-container" />
            <span className="font-mono text-xs text-outline group-hover:text-white">CASES /</span>
            <span className="font-mono text-xs font-bold text-white tracking-wide">
              {activeId}
            </span>
            <ChevronDown className="w-3.5 h-3.5 text-on-surface-variant group-hover:text-white transition-transform" />
          </div>

          {/* Case Quick Dropdown */}
          {isCaseDropdownOpen && (
            <div className="absolute top-12 left-0 w-80 glass-panel p-2 rounded-xl shadow-2xl border border-white/15 z-50 flex flex-col gap-1 max-h-96 overflow-y-auto">
              <span className="label-caps text-outline px-2 py-1">Quick Select Case ({cases.length})</span>
              {cases.slice(0, 15).map((c: Case) => (
                <button
                  key={c.case_id}
                  onClick={() => handleSelectCase(c.case_id)}
                  className={`flex items-center justify-between p-2 rounded-lg text-left transition-colors text-xs font-mono ${
                    c.case_id === activeId
                      ? 'bg-primary-container/20 text-primary border border-primary-container/40'
                      : 'text-on-surface hover:bg-white/5'
                  }`}
                >
                  <div className="flex flex-col min-w-0 pr-2">
                    <span className="font-bold text-white truncate">{c.case_id}: {c.title}</span>
                    <span className="text-[10px] text-on-surface-variant font-sans truncate">{c.concept} • {c.osi_layer}</span>
                  </div>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-surface-container text-on-surface-variant border border-white/5 shrink-0">
                    {c.severity}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Center: Command Palette Trigger Button */}
        <div className="hidden md:flex items-center">
          <button
            onClick={() => setIsCommandPaletteOpen(true)}
            className="flex items-center justify-between w-72 lg:w-96 bg-surface-container hover:bg-surface-container-high px-3.5 py-1.5 text-xs text-on-surface-variant rounded-lg border border-white/10 hover:border-white/20 transition-all font-sans group"
            aria-label="Open command palette (Ctrl+K)"
          >
            <div className="flex items-center gap-2">
              <Search className="w-4 h-4 text-outline group-hover:text-primary-container transition-colors" />
              <span>Search cases, commands, layers...</span>
            </div>
            <div className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 text-[10px] font-mono text-outline bg-black/40 border border-white/10 rounded">
                ⌘K
              </kbd>
            </div>
          </button>
        </div>

        {/* Right: Actions & Primary CTA */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/topology')}
            className="p-2 rounded-lg bg-surface-container hover:bg-surface-container-high border border-white/10 text-on-surface-variant hover:text-white transition-colors"
            title="Network Topology Graph"
            aria-label="Network Topology Diagram"
          >
            <GitFork className="w-4 h-4" />
          </button>

          <button
            onClick={() => navigate('/health')}
            className="p-2 rounded-lg bg-surface-container hover:bg-surface-container-high border border-white/10 text-on-surface-variant hover:text-white transition-colors"
            title="System Settings & Diagnostics"
            aria-label="System Health and Diagnostics"
          >
            <Settings className="w-4 h-4" />
          </button>

          {/* Primary CTA */}
          {getCtaButton()}
        </div>
      </header>

      {/* Command Palette Modal */}
      <CommandPalette
        isOpen={isCommandPaletteOpen}
        onClose={() => setIsCommandPaletteOpen(false)}
      />
    </>
  );
};
