import React, { useState, useEffect } from 'react';
import { CheckCircle2, XCircle, Terminal, Send, RefreshCw } from 'lucide-react';
import { getCases, verifyCaseFix } from '../services/api';
import CodeViewer from '../components/CodeViewer';

const PRESET_SUCCESS_VERIF = `show ip interface brief
GigabitEthernet0/0/0     192.168.1.1     YES manual up                    up
GigabitEthernet0/0/1     203.0.113.2     YES manual up                    up

ping 192.168.30.10
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 192.168.30.10, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 1/2/4 ms`;

const PRESET_FAILED_VERIF = `show ip interface brief
GigabitEthernet0/0/0.15  192.168.15.1    YES manual administratively down down

ping 192.168.15.10
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 192.168.15.10, timeout is 2 seconds:
.....
Success rate is 0 percent (0/5)`;

export default function Verification({ selectedCaseId }) {
  const [cases, setCases] = useState([]);
  const [targetCaseId, setTargetCaseId] = useState(selectedCaseId || '');
  const [output, setOutput] = useState('');
  const [verifying, setVerifying] = useState(false);
  const [result, setResult] = useState(null);

  useEffect(() => {
    getCases().then(data => {
      setCases(data);
      if (!targetCaseId && data.length > 0) {
        setTargetCaseId(data[0].id);
      }
    });
  }, [selectedCaseId]);

  const handleVerify = async (e) => {
    e.preventDefault();
    if (!targetCaseId || !output.trim()) {
      alert('Please select a target case and enter post-fix verification output.');
      return;
    }

    setVerifying(true);
    try {
      const res = await verifyCaseFix(targetCaseId, { verification_output: output });
      setResult(res);
    } catch (err) {
      console.error('Failed to run verification', err);
      alert('Error verifying fix.');
    } finally {
      setVerifying(false);
    }
  };

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      <div>
        <h2 style={{ fontSize: '1.5rem', fontWeight: '700', color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <CheckCircle2 size={24} color="#10b981" />
          <span>Post-Fix Network Verification Engine</span>
        </h2>
        <p style={{ fontSize: '0.875rem', color: '#94a3b8' }}>
          Validate that applied Cisco CLI fix commands successfully resolved network faults.
        </p>
      </div>

      {/* Preset Verification Buttons */}
      <div className="glass-card" style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
        <span style={{ fontSize: '0.8rem', fontWeight: '700', color: '#cbd5e1' }}>Load Verification Presets:</span>
        <button type="button" className="btn btn-secondary" onClick={() => setOutput(PRESET_SUCCESS_VERIF)} style={{ fontSize: '0.75rem', padding: '0.35rem 0.65rem' }}>
          + Sample Success (100% Ping Reply)
        </button>
        <button type="button" className="btn btn-secondary" onClick={() => setOutput(PRESET_FAILED_VERIF)} style={{ fontSize: '0.75rem', padding: '0.35rem 0.65rem' }}>
          + Sample Failure (Admin Down / 0% Ping)
        </button>
      </div>

      <form onSubmit={handleVerify} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        
        {/* Select Target Case */}
        <div className="glass-card">
          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '700', marginBottom: '0.5rem', color: '#cbd5e1' }}>
            Select Target Case to Verify
          </label>
          <select 
            className="select-field"
            value={targetCaseId}
            onChange={(e) => setTargetCaseId(e.target.value)}
          >
            {cases.map(c => (
              <option key={c.id} value={c.id}>
                {c.id} - {c.title} ({c.concept})
              </option>
            ))}
          </select>
        </div>

        {/* Verification Evidence Textarea */}
        <div className="glass-card">
          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '700', marginBottom: '0.5rem', color: '#cbd5e1' }}>
            Post-Fix Evidence & CLI Output
          </label>
          <textarea
            className="textarea-field"
            style={{ minHeight: '180px', color: '#a7f3d0' }}
            placeholder="Paste show output or ICMP ping results after applying configuration fixes..."
            value={output}
            onChange={(e) => setOutput(e.target.value)}
            required
          />
        </div>

        <button 
          type="submit" 
          className="btn btn-primary"
          disabled={verifying}
          style={{ padding: '0.85rem', fontSize: '1rem' }}
        >
          {verifying ? (
            <span>Analyzing Verification Telemetry...</span>
          ) : (
            <>
              <Send size={18} />
              <span>Verify Network Fix</span>
            </>
          )}
        </button>

      </form>

      {/* Verification Result Banner */}
      {result && (
        <div className="glass-card" style={{ 
          border: result.status === 'Passed' ? '2px solid #10b981' : '2px solid #f43f5e',
          background: result.status === 'Passed' ? 'rgba(16, 185, 129, 0.08)' : 'rgba(244, 63, 94, 0.08)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
            {result.status === 'Passed' ? (
              <CheckCircle2 size={32} color="#10b981" />
            ) : (
              <XCircle size={32} color="#f43f5e" />
            )}
            <div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: '700', color: result.status === 'Passed' ? '#34d399' : '#fb7185' }}>
                Verification {result.status}
              </h3>
              <p style={{ fontSize: '0.875rem', color: '#cbd5e1' }}>
                {result.explanation}
              </p>
            </div>
          </div>
          <CodeViewer title="Post-Fix Evaluated Evidence" code={result.verification_output} />
        </div>
      )}

    </div>
  );
}
