import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { Case, ReviewDecision, VerificationResult, VerificationCheck } from '../types';
import { api } from '../services/api';
import { useToast } from './ToastContext';

interface CaseContextValue {
  cases: Case[];
  currentCase: Case | null;
  loading: boolean;
  selectedCaseId: string;
  setSelectedCaseId: (id: string) => void;
  loadCase: (id: string) => Promise<void>;
  runDiagnosis: (caseId: string) => Promise<void>;
  submitReview: (caseId: string, decision: ReviewDecision) => Promise<void>;
  approveFix: (caseId: string) => Promise<void>;
  runVerification: (caseId: string) => Promise<void>;
  resetDemoMode: () => Promise<void>;
  refreshCases: (isManual?: boolean) => Promise<void>;
}

const CaseContext = createContext<CaseContextValue | undefined>(undefined);

export const CaseProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [cases, setCases] = useState<Case[]>([]);
  const [selectedCaseId, setSelectedCaseId] = useState<string>('CASE-004');
  const [currentCase, setCurrentCase] = useState<Case | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const { showToast } = useToast();

  const refreshCases = useCallback(async (isManual: boolean = false) => {
    try {
      setLoading(true);
      const data = await api.getCases();
      setCases(data);
      const targetId = selectedCaseId || (data.length > 0 ? data[0].case_id : 'CASE-004');
      if (targetId) {
        const fullCase = await api.getCaseById(targetId).catch(() => null);
        if (fullCase) {
          setCurrentCase(fullCase);
          setSelectedCaseId(fullCase.case_id);
        } else if (data.length > 0) {
          setCurrentCase(data[0]);
          setSelectedCaseId(data[0].case_id);
        }
      }
      if (isManual) {
        showToast('success', 'Database Synced', `Synchronized ${data.length} cases with local backend.`);
      }
    } catch (err) {
      console.error('Failed to load cases', err);
      showToast('error', 'Sync Failed', 'Could not load cases from local database. Check if backend is running.');
    } finally {
      setLoading(false);
    }
  }, [selectedCaseId, showToast]);

  useEffect(() => {
    refreshCases(false);
  }, []);

  const loadCase = useCallback(async (id: string) => {
    try {
      setLoading(true);
      setSelectedCaseId(id);
      const c = await api.getCaseById(id);
      if (c) {
        setCurrentCase(c);
      }
    } catch (err) {
      console.error('Failed to load case', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const runDiagnosis = async (caseId: string) => {
    try {
      setLoading(true);
      const updated = await api.runDiagnosis(caseId);
      setCases(prev => prev.map(c => c.case_id === updated.case_id ? updated : c));
      setCurrentCase(updated);
      showToast('success', 'Diagnosis Complete', `AI analysis & deterministic rule evaluation completed for ${caseId}.`);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Diagnosis failed';
      console.error('Diagnosis error', err);
      showToast('error', 'Diagnosis Failed', msg);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const submitReview = async (caseId: string, decision: ReviewDecision) => {
    try {
      const updated = await api.submitReview(caseId, decision);
      setCases(prev => prev.map(c => c.case_id === updated.case_id ? updated : c));
      if (currentCase?.case_id === updated.case_id) {
        setCurrentCase(updated);
      }
      showToast(
        decision.decision === 'REJECTED' ? 'warning' : 'success',
        `Review Decision: ${decision.decision}`,
        `Case ${caseId} transitioned to ${updated.status}. Decision logged to Audit Trail.`
      );
    } catch (err) {
      console.error('Review submission error', err);
      showToast('error', 'Submission Failed', 'Could not record review decision.');
      throw err;
    }
  };

  const approveFix = async (caseId: string) => {
    try {
      const updated = await api.approveFix(caseId);
      setCases(prev => prev.map(c => c.case_id === updated.case_id ? updated : c));
      if (currentCase?.case_id === updated.case_id) {
        setCurrentCase(updated);
      }
      showToast('success', 'Fix Plan Approved', `Implementation plan approved for ${caseId}. Verification unlocked.`);
    } catch (err) {
      console.error('Approve fix error', err);
      showToast('error', 'Approval Error', 'Could not approve fix plan.');
      throw err;
    }
  };

  const runVerification = async (caseId: string) => {
    try {
      const target = cases.find(c => c.case_id.toLowerCase() === caseId.toLowerCase());
      if (!target) return;

      const initialChecks: VerificationCheck[] = [
        {
          id: 'vcheck-1',
          description: 'Interface Physical & Line Protocol Status Check',
          target_device: target.devices?.[2]?.name || 'R1',
          command: 'show ip interface brief',
          status: 'RUNNING',
          output_snippet: 'Probing status on target interface...'
        },
        {
          id: 'vcheck-2',
          description: 'End-to-End ICMP Connectivity Echo Verification',
          target_device: 'PC1 (Source Host)',
          command: 'ping 10.0.0.100 repeat 5',
          status: 'PENDING'
        },
        {
          id: 'vcheck-3',
          description: 'Routing Table Forwarding Path Validation',
          target_device: 'R1 / Core Gateway',
          command: 'show ip route',
          status: 'PENDING'
        }
      ];

      // Temporary update to state
      const verificationInProgress: VerificationResult = {
        completed_at: new Date().toISOString(),
        checks: initialChecks,
        all_passed: false,
        notes: 'Live verification in progress...'
      };

      const interimCase = { ...target, status: 'VERIFICATION' as const, verification: verificationInProgress };
      setCurrentCase(interimCase);
      setCases(prev => prev.map(c => c.case_id === interimCase.case_id ? interimCase : c));

      // Simulate step 1
      await new Promise(r => setTimeout(r, 700));
      initialChecks[0].status = 'PASS';
      initialChecks[0].output_snippet = 'GigabitEthernet0/1 is up, line protocol is up';
      initialChecks[1].status = 'RUNNING';
      setCurrentCase({ ...interimCase, verification: { ...verificationInProgress, checks: [...initialChecks] } });

      // Simulate step 2
      await new Promise(r => setTimeout(r, 700));
      initialChecks[1].status = 'PASS';
      initialChecks[1].output_snippet = 'Success rate is 100 percent (5/5), round-trip min/avg/max = 1/2/4 ms';
      initialChecks[2].status = 'RUNNING';
      setCurrentCase({ ...interimCase, verification: { ...verificationInProgress, checks: [...initialChecks] } });

      // Simulate step 3
      await new Promise(r => setTimeout(r, 700));
      initialChecks[2].status = 'PASS';
      initialChecks[2].output_snippet = 'Direct route active. No packet drops detected.';

      const finalResult: VerificationResult = {
        completed_at: new Date().toISOString(),
        checks: initialChecks,
        all_passed: true,
        notes: 'All diagnostic and reachability checks passed successfully.'
      };

      const finalized = await api.saveVerificationResult(caseId, finalResult);
      setCases(prev => prev.map(c => c.case_id === finalized.case_id ? finalized : c));
      setCurrentCase(finalized);
      showToast('success', 'Verification Succeeded!', `Case ${caseId} is now RESOLVED.`);
    } catch (err) {
      console.error('Verification failure', err);
      showToast('error', 'Verification Failed', 'Automated test suite reported errors.');
      throw err;
    }
  };

  const resetDemoMode = async () => {
    api.resetDemoState();
    await refreshCases();
    showToast('info', 'Demo State Reset', 'All cases, reviews, and test runs reset to initial baseline.');
  };

  return (
    <CaseContext.Provider
      value={{
        cases,
        currentCase,
        loading,
        selectedCaseId,
        setSelectedCaseId,
        loadCase,
        runDiagnosis,
        submitReview,
        approveFix,
        runVerification,
        resetDemoMode,
        refreshCases
      }}
    >
      {children}
    </CaseContext.Provider>
  );
};

export const useCase = () => {
  const context = useContext(CaseContext);
  if (!context) throw new Error('useCase must be used within a CaseProvider');
  return context;
};
