import React from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  FolderGit2,
  Search,
  Filter,
  ArrowUpDown,
  ArrowRight,
  Cpu,
  Inbox,
  Download,
  AlertTriangle,
  RotateCcw,
  WifiOff
} from 'lucide-react';
import { useCases } from '../hooks/useCases';
import { useCase } from '../context/CaseContext';
import { useDocumentTitle } from '../hooks/useDocumentTitle';
import { GlassPanel } from '../components/common/GlassWrappers';
import { StatusBadge } from '../components/common/StatusBadge';
import { SkeletonLoader } from '../components/common/SkeletonLoader';
import { Case } from '../types';

export const CaseList: React.FC = () => {
  useDocumentTitle('Case Explorer — 35 Cisco Incidents');
  const [searchParams] = useSearchParams();
  const {
    cases,
    filteredCases,
    loading,
    error,
    categories,
    searchQuery,
    setSearchQuery,
    severityFilter,
    setSeverityFilter,
    categoryFilter,
    setCategoryFilter,
    sortField,
    toggleSort,
    exportToCsv,
    isSimulatingError,
    toggleSimulateError,
    retry
  } = useCases({
    initialSearch: searchParams.get('q') || ''
  });

  const { setSelectedCaseId } = useCase();
  const navigate = useNavigate();

  const handleOpenCase = (id: string) => {
    setSelectedCaseId(id);
    navigate('/workbench');
  };

  return (
    <div className="space-y-6 pb-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <FolderGit2 className="w-7 h-7 text-primary-container" />
            Case Explorer &amp; Diagnostic Archive
          </h1>
          <p className="text-xs sm:text-sm text-on-surface-variant mt-1">
            Browse 35 seed Cisco lab incidents, inspect grounded root-cause citations, and export reports.
          </p>
        </div>

        <div className="flex items-center gap-2.5 flex-wrap">
          {/* Simulate Network Failure Toggle */}
          <button
            onClick={toggleSimulateError}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold border flex items-center gap-1.5 transition-all ${
              isSimulatingError
                ? 'bg-red-950/60 border-red-500 text-red-300 shadow-glow-critical'
                : 'bg-white/5 border-white/10 text-outline hover:text-white'
            }`}
            title="Simulate 503 Network Error for Resilience Testing"
            aria-label="Toggle network error simulation"
          >
            <WifiOff className="w-3.5 h-3.5" />
            <span>{isSimulatingError ? 'Simulating Error' : 'Simulate API Error'}</span>
          </button>

          {/* Export to CSV CTA */}
          <button
            onClick={exportToCsv}
            disabled={filteredCases.length === 0}
            className="px-3.5 py-1.5 rounded-lg text-xs font-bold font-sans bg-primary-container hover:bg-orange-500 text-white shadow-glow-critical flex items-center gap-1.5 transition-all active:scale-95 disabled:opacity-50"
            title="Export filtered dataset to cases.csv matching assignment schema"
            aria-label="Export filtered cases to CSV"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* Error state handling if API fails */}
      {error && (
        <GlassPanel className="p-6 rounded-xl border border-red-500/50 bg-red-950/30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 animate-fadeIn">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-red-500/20 border border-red-500/40 flex items-center justify-center text-red-400 shrink-0">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Network Telemetry Ingestion Failed</h3>
              <p className="text-xs text-on-surface-variant mt-0.5">{error}</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={retry}
              className="px-3.5 py-1.5 rounded-lg text-xs font-mono font-semibold bg-red-500 hover:bg-red-400 text-white flex items-center gap-1.5 transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Retry Sync</span>
            </button>
            {isSimulatingError && (
              <button
                onClick={toggleSimulateError}
                className="px-3 py-1.5 rounded-lg text-xs font-mono bg-white/10 hover:bg-white/15 text-white border border-white/10"
              >
                Disable Simulation
              </button>
            )}
          </div>
        </GlassPanel>
      )}

      {/* Filter and Search Bar */}
      <GlassPanel className="p-4 border border-white/10 space-y-3">
        <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
          {/* Search Input */}
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-outline absolute left-3 top-2.5 pointer-events-none" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by ID, title, symptom, layer, concept, or command..."
              className="w-full bg-surface-container pl-9 pr-4 py-2 text-xs text-white rounded-lg border border-white/10 focus:outline-none focus:border-primary-container focus:ring-1 focus:ring-primary-container font-sans"
              aria-label="Search cases filter"
            />
          </div>

          {/* Category Dropdown */}
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-outline" />
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="bg-surface-container text-xs text-white px-3 py-2 rounded-lg border border-white/10 focus:outline-none focus:border-primary-container font-mono"
              aria-label="Filter by issue category"
            >
              {categories.map(cat => (
                <option key={cat} value={cat}>
                  Category: {cat.replace(/_/g, ' ')}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Severity Filter Chips */}
        <div className="flex items-center gap-2 flex-wrap pt-2 border-t border-white/5 text-xs font-mono">
          <span className="text-outline text-[11px] uppercase">Severity:</span>
          {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map(sev => (
            <button
              key={sev}
              onClick={() => setSeverityFilter(sev)}
              className={`px-2.5 py-1 rounded text-xs transition-colors font-semibold ${
                severityFilter === sev
                  ? 'bg-primary-container text-white shadow-glow-critical'
                  : 'bg-surface-container text-on-surface-variant hover:text-white border border-white/5'
              }`}
              aria-label={`Filter by severity ${sev}`}
            >
              {sev}
            </button>
          ))}
          <span className="text-outline text-[11px] ml-auto">
            Showing <strong className="text-white">{filteredCases.length}</strong> of {cases.length}
          </span>
        </div>
      </GlassPanel>

      {/* Case Table / Loading / Empty State */}
      {loading ? (
        <div className="space-y-3">
          <SkeletonLoader className="h-12 rounded-xl" />
          <SkeletonLoader className="h-64 rounded-xl" />
        </div>
      ) : filteredCases.length === 0 ? (
        <GlassPanel className="p-12 text-center border border-white/10 flex flex-col items-center justify-center space-y-3">
          <div className="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center text-outline">
            <Inbox className="w-6 h-6" />
          </div>
          <h3 className="text-base font-bold text-white">No Matching Incidents Found</h3>
          <p className="text-xs text-on-surface-variant max-w-sm">
            No Cisco telemetry cases match your current search queries and filters. Try clearing or relaxing your filter constraints.
          </p>
          <button
            onClick={() => {
              setSearchQuery('');
              setSeverityFilter('ALL');
              setCategoryFilter('ALL');
            }}
            className="px-3.5 py-1.5 rounded-lg text-xs font-mono bg-white/10 hover:bg-white/15 text-white border border-white/10 transition-colors"
          >
            Reset All Filters
          </button>
        </GlassPanel>
      ) : (
        <GlassPanel className="p-4 border border-white/10 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono" aria-label="Cisco Incidents Table">
              <thead>
                <tr className="border-b border-white/10 text-outline select-none">
                  <th
                    onClick={() => toggleSort('case_id')}
                    className="pb-3 font-semibold cursor-pointer hover:text-white transition-colors"
                  >
                    <div className="flex items-center gap-1">
                      <span>CASE ID</span>
                      <ArrowUpDown className="w-3 h-3" />
                    </div>
                  </th>
                  <th className="pb-3 font-semibold">TITLE &amp; SYMPTOM</th>
                  <th
                    onClick={() => toggleSort('osi_layer')}
                    className="pb-3 font-semibold cursor-pointer hover:text-white transition-colors"
                  >
                    <div className="flex items-center gap-1">
                      <span>OSI LAYER</span>
                      <ArrowUpDown className="w-3 h-3" />
                    </div>
                  </th>
                  <th className="pb-3 font-semibold">CONCEPT</th>
                  <th
                    onClick={() => toggleSort('severity')}
                    className="pb-3 font-semibold cursor-pointer hover:text-white transition-colors"
                  >
                    <div className="flex items-center gap-1">
                      <span>SEVERITY</span>
                      <ArrowUpDown className="w-3 h-3" />
                    </div>
                  </th>
                  <th className="pb-3 font-semibold">FUSION</th>
                  <th className="pb-3 font-semibold">STATUS</th>
                  <th className="pb-3 font-semibold text-right">ACTION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {filteredCases.map((c: Case) => (
                  <tr
                    key={c.case_id}
                    className="hover:bg-white/[0.03] transition-colors group cursor-pointer"
                    onClick={() => handleOpenCase(c.case_id)}
                  >
                    <td className="py-3.5 font-bold text-primary-container whitespace-nowrap">
                      {c.case_id}
                    </td>
                    <td className="py-3.5 max-w-xs sm:max-w-md pr-4">
                      <div className="text-white font-sans font-semibold text-xs group-hover:text-primary transition-colors">
                        {c.title}
                      </div>
                      <div className="text-[11px] text-on-surface-variant font-sans truncate mt-0.5">
                        {c.symptom}
                      </div>
                    </td>
                    <td className="py-3.5 whitespace-nowrap">
                      <span className="text-secondary bg-secondary/10 px-2 py-0.5 rounded border border-secondary/30 text-[11px]">
                        {c.osi_layer}
                      </span>
                    </td>
                    <td className="py-3.5 font-sans font-medium text-white/90 whitespace-nowrap">
                      <span className="bg-white/5 px-2 py-0.5 rounded border border-white/5 text-[11px]">
                        {c.concept}
                      </span>
                    </td>
                    <td className="py-3.5 whitespace-nowrap">
                      <StatusBadge status={c.severity} size="sm" />
                    </td>
                    <td className="py-3.5 whitespace-nowrap">
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
                    <td className="py-3.5 whitespace-nowrap">
                      <StatusBadge status={c.status} size="sm" />
                    </td>
                    <td className="py-3.5 text-right whitespace-nowrap" onClick={(e) => e.stopPropagation()}>
                      <button
                        onClick={() => handleOpenCase(c.case_id)}
                        className="px-3 py-1.5 rounded-lg bg-surface-container hover:bg-primary-container hover:text-white text-on-surface-variant border border-white/10 transition-all font-sans font-semibold text-xs flex items-center gap-1.5 ml-auto"
                        aria-label={`Diagnose case ${c.case_id}`}
                      >
                        <Cpu className="w-3.5 h-3.5 text-primary" />
                        <span>Diagnose</span>
                        <ArrowRight className="w-3 h-3" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </GlassPanel>
      )}
    </div>
  );
};
