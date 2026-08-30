import { useState, useMemo, useCallback, useEffect } from 'react';
import { Case, Severity } from '../types';
import { api } from '../services/api';
import { useToast } from '../context/ToastContext';

export interface UseCasesOptions {
  initialSearch?: string;
  initialSeverity?: string;
  initialCategory?: string;
}

const severityOrder: Record<Severity, number> = {
  CRITICAL: 4,
  HIGH: 3,
  MEDIUM: 2,
  LOW: 1
};

export function useCases(options: UseCasesOptions = {}) {
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>(options.initialSearch || '');
  const [severityFilter, setSeverityFilter] = useState<string>(options.initialSeverity || 'ALL');
  const [categoryFilter, setCategoryFilter] = useState<string>(options.initialCategory || 'ALL');
  const [sortField, setSortField] = useState<'case_id' | 'severity' | 'osi_layer'>('case_id');
  const [sortAsc, setSortAsc] = useState<boolean>(true);
  const [isSimulatingError, setIsSimulatingError] = useState<boolean>(false);
  const { showToast } = useToast();

  const fetchCases = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getCases();
      setCases(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to fetch telemetry cases';
      setError(msg);
      showToast('error', 'Network Telemetry Error', msg);
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  useEffect(() => {
    fetchCases();
  }, [fetchCases]);

  const categories = useMemo(() => {
    const set = new Set<string>();
    cases.forEach(c => set.add(c.category));
    return ['ALL', ...Array.from(set)];
  }, [cases]);

  const filteredAndSortedCases = useMemo(() => {
    return cases
      .filter(c => {
        // Search filter
        if (searchQuery.trim()) {
          const q = searchQuery.toLowerCase();
          const matches =
            c.case_id.toLowerCase().includes(q) ||
            c.title.toLowerCase().includes(q) ||
            c.symptom.toLowerCase().includes(q) ||
            c.concept.toLowerCase().includes(q) ||
            c.osi_layer.toLowerCase().includes(q) ||
            c.category.toLowerCase().includes(q);
          if (!matches) return false;
        }

        // Severity filter
        if (severityFilter !== 'ALL' && c.severity !== severityFilter) {
          return false;
        }

        // Category filter
        if (categoryFilter !== 'ALL' && c.category !== categoryFilter) {
          return false;
        }

        return true;
      })
      .sort((a, b) => {
        if (sortField === 'severity') {
          const diff = severityOrder[a.severity] - severityOrder[b.severity];
          return sortAsc ? diff : -diff;
        }
        if (sortField === 'osi_layer') {
          return sortAsc
            ? a.osi_layer.localeCompare(b.osi_layer)
            : b.osi_layer.localeCompare(a.osi_layer);
        }
        return sortAsc
          ? a.case_id.localeCompare(b.case_id)
          : b.case_id.localeCompare(a.case_id);
      });
  }, [cases, searchQuery, severityFilter, categoryFilter, sortField, sortAsc]);

  const toggleSort = (field: 'case_id' | 'severity' | 'osi_layer') => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(false);
    }
  };

  const toggleSimulateError = () => {
    const nextVal = !isSimulatingError;
    setIsSimulatingError(nextVal);
    api.setSimulateApiError(nextVal);
    fetchCases();
  };

  const exportToCsv = useCallback(() => {
    if (filteredAndSortedCases.length === 0) {
      showToast('warning', 'Export Empty', 'No cases to export in current filter.');
      return;
    }

    // CSV header matching graded assignment format
    const headers = [
      'case_id',
      'title',
      'category',
      'symptom',
      'expected_fault',
      'osi_layer',
      'concept',
      'severity'
    ];

    const rows = filteredAndSortedCases.map(c => [
      `"${c.case_id.replace(/"/g, '""')}"`,
      `"${c.title.replace(/"/g, '""')}"`,
      `"${c.category.replace(/"/g, '""')}"`,
      `"${c.symptom.replace(/"/g, '""')}"`,
      `"${c.expected_fault.replace(/"/g, '""')}"`,
      `"${c.osi_layer.replace(/"/g, '""')}"`,
      `"${c.concept.replace(/"/g, '""')}"`,
      `"${c.severity.replace(/"/g, '""')}"`
    ]);

    const csvContent = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `netsage_cases_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    showToast(
      'success',
      'Export Complete',
      `Exported ${filteredAndSortedCases.length} cases to cases.csv matching submission schema.`
    );
  }, [filteredAndSortedCases, showToast]);

  return {
    cases,
    filteredCases: filteredAndSortedCases,
    totalCount: cases.length,
    filteredCount: filteredAndSortedCases.length,
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
    sortAsc,
    toggleSort,
    exportToCsv,
    isSimulatingError,
    toggleSimulateError,
    retry: fetchCases
  };
}
