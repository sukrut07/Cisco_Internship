import React, { useState } from 'react';
import { Cpu, Play, Terminal, ShieldCheck } from 'lucide-react';
import RuleCheckBadges from '../components/RuleCheckBadges';
import { runRuleCheckSandbox } from '../services/api';

const SAMPLE_CLI_PAYLOAD = `=== Switch-2 show vlan brief ===
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Fa0/1, Fa0/2, Fa0/3, Fa0/4

=== Switch-2 show interfaces Fa0/10 switchport ===
Access Mode VLAN: 30 (inactive)

=== Router Fa0/0 show ip interface brief ===
GigabitEthernet0/0.15  192.168.15.1   YES manual administratively down down

=== Syslog Log ===
%IP-4-DUPADDR: Duplicate address 192.168.5.10 on FastEthernet0/10`;

export default function RuleCheckerPage() {
  const [cliText, setCliText] = useState(SAMPLE_CLI_PAYLOAD);
  const [sourceIp, setSourceIp] = useState('');
  const [gateway, setGateway] = useState('');
  const [subnetMask, setSubnetMask] = useState('');

  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  const handleRunChecks = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await runRuleCheckSandbox({
        show_outputs: cliText,
        source_ip: sourceIp || null,
        gateway: gateway || null,
        subnet_mask: subnetMask || null
      });
      setResults(res);
    } catch (err) {
      console.error('Failed to run rule checker sandbox', err);
      alert('Error running deterministic rule check.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      <div>
        <h2 style={{ fontSize: '1.5rem', fontWeight: '700', color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Cpu size={24} color="#06b6d4" />
          <span>Deterministic Python Rule Checker Sandbox</span>
        </h2>
        <p style={{ fontSize: '0.875rem', color: '#94a3b8' }}>
          Test hardcoded rule logic for Duplicate IPs, Gateway Mismatches, Down Interfaces, Missing VLANs, and Missing Routes without calling AI models.
        </p>
      </div>

      <form onSubmit={handleRunChecks} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        
        <div className="glass-card">
          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '700', marginBottom: '0.5rem', color: '#cbd5e1' }}>
            Cisco CLI Show Outputs & Logs
          </label>
          <textarea
            className="textarea-field"
            style={{ minHeight: '200px', color: '#a7f3d0' }}
            value={cliText}
            onChange={(e) => setCliText(e.target.value)}
            required
          />
        </div>

        <div className="glass-card">
          <h4 style={{ fontSize: '0.85rem', fontWeight: '700', color: '#cbd5e1', marginBottom: '0.75rem' }}>
            Optional Structured Network Parameters
          </h4>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem' }}>
            <div>
              <label style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Host Source IP</label>
              <input type="text" className="input-field" placeholder="192.168.1.50" value={sourceIp} onChange={e => setSourceIp(e.target.value)} />
            </div>
            <div>
              <label style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Default Gateway</label>
              <input type="text" className="input-field" placeholder="192.168.2.1" value={gateway} onChange={e => setGateway(e.target.value)} />
            </div>
            <div>
              <label style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Subnet Mask</label>
              <input type="text" className="input-field" placeholder="255.255.255.0" value={subnetMask} onChange={e => setSubnetMask(e.target.value)} />
            </div>
          </div>
        </div>

        <button 
          type="submit" 
          className="btn btn-primary"
          disabled={loading}
          style={{ padding: '0.85rem', fontSize: '1rem' }}
        >
          {loading ? 'Evaluating Rules...' : 'Run Python Rule Checker'}
        </button>

      </form>

      {results && (
        <div className="glass-card">
          <RuleCheckBadges ruleChecks={results} />
        </div>
      )}

    </div>
  );
}
