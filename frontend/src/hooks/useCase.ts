import { useState, useEffect, useCallback } from 'react';
import { Case } from '../types';
import { api } from '../services/api';
import { useCase as useCaseContext } from '../context/CaseContext';

export function useCase(caseId?: string) {
  const context = useCaseContext();
  const [caseData, setCaseData] = useState<Case | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const targetId = caseId || context.selectedCaseId || 'CASE-004';

  const fetchCase = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getCaseById(targetId);
      if (data) {
        setCaseData(data);
      } else {
        setError(`Case ${targetId} not found`);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load case');
    } finally {
      setLoading(false);
    }
  }, [targetId]);

  useEffect(() => {
    fetchCase();
  }, [fetchCase]);

  // Keep synced with context's currentCase if it matches targetId
  const activeCase = (context.currentCase && context.currentCase.case_id.toLowerCase() === targetId.toLowerCase())
    ? context.currentCase
    : caseData;

  return {
    currentCase: activeCase,
    loading,
    error,
    refresh: fetchCase,
    submitReview: context.submitReview,
    approveFix: context.approveFix,
    runVerification: context.runVerification
  };
}
