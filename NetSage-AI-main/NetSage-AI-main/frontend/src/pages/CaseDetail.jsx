import React, { useState, useEffect } from 'react';
import { 
  CheckCircle, 
  Edit3, 
  XCircle, 
  Cpu, 
  Sparkles, 
  Terminal, 
  ShieldCheck, 
  CheckCircle2, 
  Layers, 
  RefreshCw, 
  AlertTriangle,
  ArrowRight
} from 'lucide-react';
import CodeViewer from '../components/CodeViewer';
import RuleCheckBadges from '../components/RuleCheckBadges';
import { getCaseHistory, diagnoseCase, submitHumanReview } from '../services/api';

export default function CaseDetail({ caseId, setActivePage }) {
  const [history, setHistory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [diagnosing, setDiagnosing] = useState(false);

  // Review Modals State
  const [showEditModal, setShowEditModal] = useState(false);
  const [showRejectModal, setShowRejectModal] = useState(false);

  // Form Fields for Edit
  const [corrRootCause, setCorrRootCause] = useState('');
  const [corrOsiLayer, setCorrOsiLayer] = useState('');
  const [corrExplanation, setCorrExplanation] = useState('');
  const [corrFix, setCorrFix] = useState('');
  const [editComments, setEditComments] = useState('');

  // Form Fields for Reject
  const [rejectReason, setRejectReason] = useState('');
  const [reviewerName, setReviewerName] = useState('Senior NetEng Reviewer');

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const data = await getCaseHistory(caseId);
      setHistory(data);
    } catch (err) {
      console.error('Failed to fetch case history', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (caseId) {
      fetchHistory();
    }
  }, [caseId]);

  const handleRunDiagnosis = async () => {
    setDiagnosing(true);
    try {
      await diagnoseCase(caseId);
      await fetchHistory();
    } catch (err) {
      console.error('Failed to run diagnosis', err);
      alert('Error running AI diagnosis.');
    } finally {
      setDiagnosing(false);
    }
  };

  const handleAccept = async () => {
    try {
      await submitHumanReview(caseId, {
        decision: 'ACCEPT',
        reviewer_comments: 'Accepted AI suggested root cause and fix steps.',
        reviewer_name: reviewerName
      });
      await fetchHistory();
      alert('Human Decision recorded: Diagnosis ACCEPTED.');
    } catch (err) {
      console.error('Failed to accept diagnosis', err);
    }
  };

  const handleEditSubmit = async (e) => {
    e.preventDefault();
    try {
      await submitHumanReview(caseId, {
        decision: 'EDIT',
        corrected_root_cause: corrRootCause,
        corrected_osi_layer: corrOsiLayer,
        corrected_explanation: corrExplanation,
        corrected_fix: corrFix,
        reviewer_comments: editComments,
        reviewer_name: reviewerName
      });
      setShowEditModal(false);
      await fetchHistory();
      alert('Human Decision recorded: Diagnosis EDITED & Corrected.');
    } catch (err) {
      console.error('Failed to submit edited diagnosis', err);
    }
  };

  const handleRejectSubmit = async (e) => {
    e.preventDefault();
    if (!rejectReason.trim()) {
      alert('Please provide a reason for rejecting the diagnosis.');
      return;
    }

    try {
      await submitHumanReview(caseId, {
        decision: 'REJECT',
        reviewer_comments: rejectReason,
        reviewer_name: reviewerName
      });
      setShowRejectModal(false);
      await fetchHistory();
      alert('Human Decision recorded: Diagnosis REJECTED.');
    } catch (err) {
      console.error('Failed to reject diagnosis', err);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <RefreshCw className="animate-spin" size={32} color="#06b6d4" />
        <span style={{ marginLeft: '0.75rem', color: '#94a3b8' }}>Loading Case Telemetry & AI Diagnosis...</span>
      </div>
    );
  }

  const c = history?.case;
  const latestDiag = history?.diagnoses?.[0];
  const ruleChecks = history?.rule_checks || [];
  const reviews = history?.reviews || [];
  const latestReview = reviews[0];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* Header & Case Title */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.25rem' }}>
            <span style={{ fontFamily: 'Fira Code', fontWeight: '700', color: '#06b6d4', fontSize: '1rem' }}>
              {c?.id}
            </span>
            <span className="badge badge-info">{c?.concept}</span>
            <span className={`badge ${c?.severity === 'Critical' ? 'badge-fail' : c?.severity === 'High' ? 'badge-warning' : 'badge-info'}`}>
              {c?.severity} Severity
            </span>
            
            {/* Human Review Status Badge */}
            {latestReview ? (
              <span className={`badge ${latestReview.decision === 'ACCEPT' ? 'badge-human' : latestReview.decision === 'EDIT' ? 'badge-warning' : 'badge-fail'}`}>
                Human {latestReview.decision}ED
              </span>
            ) : (
              <span className="badge badge-warning">Awaiting Human Review</span>
            )}
          </div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: '700', color: '#f8fafc' }}>
            {c?.title}
          </h2>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button className="btn btn-secondary" onClick={handleRunDiagnosis} disabled={diagnosing}>
            <RefreshCw size={16} className={diagnosing ? 'animate-spin' : ''} />
            <span>Re-run Diagnosis</span>
          </button>
          <button className="btn btn-primary" onClick={() => setActivePage('verification')}>
            <span>Verify Network Fix</span>
            <ArrowRight size={16} />
          </button>
        </div>
      </div>

      {/* Case Evidence Summary Card */}
      <div className="glass-card">
        <h3 style={{ fontSize: '1rem', fontWeight: '700', color: '#f1f5f9', marginBottom: '0.75rem' }}>
          Case Evidence & Symptoms
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
          <div>
            <span style={{ fontSize: '0.75rem', color: '#94a3b8', fontWeight: '600' }}>REPORTED SYMPTOM</span>
            <p style={{ fontSize: '0.9rem', color: '#cbd5e1', marginTop: '0.25rem' }}>{c?.symptom}</p>
          </div>
          <div>
            <span style={{ fontSize: '0.75rem', color: '#94a3b8', fontWeight: '600' }}>TOPOLOGY NOTES</span>
            <p style={{ fontSize: '0.9rem', color: '#cbd5e1', marginTop: '0.25rem', fontFamily: 'Fira Code' }}>{c?.topology}</p>
          </div>
        </div>
      </div>

      {/* Cisco CLI Show Outputs */}
      <CodeViewer title="Evidence: Cisco CLI Show Command Outputs" code={c?.show_outputs} />

      {/* Side-by-Side Analysis Engine Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(480px, 1fr))', gap: '1.25rem' }}>
        
        {/* Left Column: Python Rule Checker Findings */}
        <div className="glass-card">
          <RuleCheckBadges ruleChecks={ruleChecks} />
        </div>

        {/* Right Column: AI Suggested Diagnosis */}
        <div className="glass-card" style={{ border: '1px solid rgba(6, 182, 212, 0.4)', background: 'linear-gradient(180deg, #131b2e 0%, #0d1527 100%)' }}>
          
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span className="badge badge-ai" style={{ fontSize: '0.75rem', padding: '0.3rem 0.65rem' }}>
                <Sparkles size={14} /> AI Suggested
              </span>
              <span style={{ fontSize: '0.85rem', fontWeight: '600', color: '#94a3b8' }}>
                Confidence: <strong style={{ color: '#06b6d4' }}>{latestDiag?.confidence || 80}% ({latestDiag?.confidence_level || 'High'})</strong>
              </span>
            </div>
            <span className="badge badge-info">{latestDiag?.osi_layer || 'Layer 3 (Network)'}</span>
          </div>

          {!latestDiag ? (
            <div style={{ textAlign: 'center', padding: '2rem', color: '#64748b' }}>
              No AI diagnosis generated yet. Click 'Re-run Diagnosis'.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              
              {/* Root Cause */}
              <div>
                <span style={{ fontSize: '0.75rem', fontWeight: '700', color: '#94a3b8', textTransform: 'uppercase' }}>Identified Root Cause</span>
                <p style={{ fontSize: '1rem', fontWeight: '600', color: '#f8fafc', marginTop: '0.25rem', padding: '0.75rem', background: 'rgba(6, 182, 212, 0.1)', borderRadius: '0.5rem', borderLeft: '4px solid #06b6d4' }}>
                  {latestDiag.root_cause}
                </p>
              </div>

              {/* Evidence Cited */}
              <div>
                <span style={{ fontSize: '0.75rem', fontWeight: '700', color: '#94a3b8', textTransform: 'uppercase' }}>Evidence Cited</span>
                <ul style={{ listStyle: 'none', paddingLeft: 0, marginTop: '0.35rem', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                  {latestDiag.evidence?.map((ev, idx) => (
                    <li key={idx} style={{ fontSize: '0.825rem', color: '#cbd5e1', display: 'flex', alignItems: 'flex-start', gap: '0.4rem' }}>
                      <span style={{ color: '#06b6d4' }}>•</span>
                      <span>{ev}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Next Recommended Commands & Fix Steps */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                <div style={{ background: '#0f172a', padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #1e293b' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: '700', color: '#60a5fa' }}>NEXT CISCO COMMANDS</span>
                  <div style={{ fontSize: '0.8rem', color: '#a7f3d0', fontFamily: 'Fira Code', marginTop: '0.25rem' }}>
                    {latestDiag.next_commands?.map((cmd, i) => (
                      <div key={i}># {cmd}</div>
                    ))}
                  </div>
                </div>

                <div style={{ background: '#0f172a', padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #1e293b' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: '700', color: '#34d399' }}>SUGGESTED FIX STEPS</span>
                  <div style={{ fontSize: '0.8rem', color: '#e2e8f0', marginTop: '0.25rem' }}>
                    {latestDiag.fix_steps?.map((step, i) => (
                      <div key={i}>{i + 1}. {step}</div>
                    ))}
                  </div>
                </div>
              </div>

            </div>
          )}

        </div>

      </div>

      {/* Human Review Decision Banner & Action Buttons */}
      <div className="glass-card" style={{ background: 'linear-gradient(90deg, #131b2e 0%, #1e293b 100%)', border: '1px solid #3b82f6' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: '700', color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <ShieldCheck size={20} color="#3b82f6" />
              <span>Human Engineering Review (Mandatory Oversight)</span>
            </h3>
            <p style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
              AI diagnosis is never final authority. Senior Network Engineers must validate findings before applying configuration fixes.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button className="btn btn-accept" onClick={handleAccept}>
              <CheckCircle size={18} />
              <span>ACCEPT</span>
            </button>

            <button className="btn btn-edit" onClick={() => {
              setCorrRootCause(latestDiag?.root_cause || '');
              setCorrOsiLayer(latestDiag?.osi_layer || 'Layer 3 (Network)');
              setCorrFix(latestDiag?.fix_steps?.join('\n') || '');
              setShowEditModal(true);
            }}>
              <Edit3 size={18} />
              <span>EDIT</span>
            </button>

            <button className="btn btn-reject" onClick={() => setShowRejectModal(true)}>
              <XCircle size={18} />
              <span>REJECT</span>
            </button>
          </div>
        </div>

        {/* Existing Human Decision Log */}
        {latestReview && (
          <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid #334155', fontSize: '0.85rem' }}>
            <span style={{ fontWeight: '700', color: '#f1f5f9' }}>Recorded Human Review Decision: </span>
            <span className={`badge ${latestReview.decision === 'ACCEPT' ? 'badge-human' : latestReview.decision === 'EDIT' ? 'badge-warning' : 'badge-fail'}`}>
              {latestReview.decision}
            </span>
            <span style={{ marginLeft: '0.75rem', color: '#94a3b8' }}>
              by {latestReview.reviewer_name} on {new Date(latestReview.created_at).toLocaleString()}
            </span>
            {latestReview.reviewer_comments && (
              <p style={{ color: '#cbd5e1', fontStyle: 'italic', marginTop: '0.35rem' }}>
                "{latestReview.reviewer_comments}"
              </p>
            )}
          </div>
        )}
      </div>

      {/* EDIT MODAL */}
      {showEditModal && (
        <div className="modal-backdrop">
          <div className="modal-content">
            <h3 style={{ fontSize: '1.25rem', fontWeight: '700', color: '#f8fafc', marginBottom: '1rem' }}>
              Edit & Correct AI Diagnosis
            </h3>
            <form onSubmit={handleEditSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ fontSize: '0.8rem', color: '#cbd5e1', fontWeight: '600' }}>Corrected Root Cause</label>
                <textarea className="textarea-field" value={corrRootCause} onChange={e => setCorrRootCause(e.target.value)} required />
              </div>
              <div>
                <label style={{ fontSize: '0.8rem', color: '#cbd5e1', fontWeight: '600' }}>Corrected OSI Layer</label>
                <select className="select-field" value={corrOsiLayer} onChange={e => setCorrOsiLayer(e.target.value)}>
                  {['Layer 1 (Physical)', 'Layer 2 (Data Link)', 'Layer 3 (Network)', 'Layer 4 (Transport)', 'Layer 7 (Application)'].map(l => (
                    <option key={l} value={l}>{l}</option>
                  ))}
                </select>
              </div>
              <div>
                <label style={{ fontSize: '0.8rem', color: '#cbd5e1', fontWeight: '600' }}>Corrected Fix Steps</label>
                <textarea className="textarea-field" value={corrFix} onChange={e => setCorrFix(e.target.value)} />
              </div>
              <div>
                <label style={{ fontSize: '0.8rem', color: '#cbd5e1', fontWeight: '600' }}>Reviewer Comments / Rationale for Correction</label>
                <textarea className="textarea-field" style={{ minHeight: '70px' }} placeholder="Explain why the AI diagnosis was modified..." value={editComments} onChange={e => setEditComments(e.target.value)} required />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '0.5rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowEditModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-edit">Save Correction & Record Decision</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* REJECT MODAL */}
      {showRejectModal && (
        <div className="modal-backdrop">
          <div className="modal-content">
            <h3 style={{ fontSize: '1.25rem', fontWeight: '700', color: '#f43f5e', marginBottom: '1rem' }}>
              Reject AI Diagnosis
            </h3>
            <form onSubmit={handleRejectSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ fontSize: '0.8rem', color: '#cbd5e1', fontWeight: '600' }}>Reason for Rejection *</label>
                <textarea className="textarea-field" placeholder="Provide clear technical rationale for why the AI diagnosis was rejected..." value={rejectReason} onChange={e => setRejectReason(e.target.value)} required />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '0.5rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowRejectModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-reject">Submit Rejection</button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
