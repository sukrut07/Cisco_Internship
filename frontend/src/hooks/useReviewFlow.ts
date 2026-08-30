import { useState, useEffect, useCallback } from 'react';
import { Case } from '../types';
import { useCase } from '../context/CaseContext';

export function useReviewFlow(targetCase: Case | null) {
  const { submitReview: submitReviewContext, approveFix: approveFixContext } = useCase();

  const [decision, setDecision] = useState<'ACCEPTED' | 'EDITED' | 'REJECTED'>('ACCEPTED');
  const [reviewerName, setReviewerName] = useState<string>('Senior Network Architect');
  const [notes, setNotes] = useState<string>('');
  const [editedRootCause, setEditedRootCause] = useState<string>('');
  const [fixSteps, setFixSteps] = useState<string[]>([]);
  const [newStep, setNewStep] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  useEffect(() => {
    if (targetCase) {
      setEditedRootCause(targetCase.ai_diagnosis.root_cause);
      setFixSteps([...targetCase.ai_diagnosis.recommended_fix]);
      if (targetCase.review) {
        setDecision(targetCase.review.decision);
        setReviewerName(targetCase.review.reviewer);
        setNotes(targetCase.review.notes);
      }
    }
  }, [targetCase]);

  const addFixStep = useCallback(() => {
    if (newStep.trim()) {
      setFixSteps(prev => [...prev, newStep.trim()]);
      setNewStep('');
    }
  }, [newStep]);

  const removeFixStep = useCallback((index: number) => {
    setFixSteps(prev => prev.filter((_, i) => i !== index));
  }, []);

  const handleRecordReview = useCallback(async () => {
    if (!targetCase) return;
    try {
      setIsSubmitting(true);
      await submitReviewContext(targetCase.case_id, {
        decision,
        reviewer: reviewerName,
        timestamp: new Date().toISOString(),
        notes: notes || (decision === 'ACCEPTED' ? 'Approved AI root cause and remediation sequence.' : 'Engineer adjustment applied.'),
        edited_root_cause: decision === 'EDITED' ? editedRootCause : undefined,
        edited_fix: fixSteps
      });
    } finally {
      setIsSubmitting(false);
    }
  }, [targetCase, decision, reviewerName, notes, editedRootCause, fixSteps, submitReviewContext]);

  const handleApproveFix = useCallback(async () => {
    if (!targetCase) return;
    try {
      setIsSubmitting(true);
      await approveFixContext(targetCase.case_id);
    } finally {
      setIsSubmitting(false);
    }
  }, [targetCase, approveFixContext]);

  const isApproved = targetCase?.status === 'FIX_APPROVED' || targetCase?.status === 'VERIFICATION' || targetCase?.status === 'RESOLVED';
  const hasDecision = targetCase?.status === 'ACCEPTED' || targetCase?.status === 'EDITED' || isApproved;

  return {
    decision,
    setDecision,
    reviewerName,
    setReviewerName,
    notes,
    setNotes,
    editedRootCause,
    setEditedRootCause,
    fixSteps,
    newStep,
    setNewStep,
    addFixStep,
    removeFixStep,
    isSubmitting,
    isApproved,
    hasDecision,
    handleRecordReview,
    handleApproveFix
  };
}
