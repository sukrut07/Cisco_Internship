import React, { useState } from 'react';
import { Terminal, Send, Sparkles, Layers, Cpu, Server, Monitor, ShieldAlert } from 'lucide-react';
import { createCase, diagnoseCase } from '../services/api';

const SAMPLE_TEMPLATES = [
  {
    title: "PC cannot access server in VLAN 30",
    symptom: "PC-1 in VLAN 10 cannot ping Server-1 in VLAN 30. Switch logs indicate VLAN 30 does not exist on Access Switch 2.",
    topology: "PC-1 (192.168.10.10) -> Switch-1 -> Switch-2 -> Server-1 (192.168.30.50)",
    concept: "VLAN",
    severity: "High",
    show_outputs: `=== Switch-2 show vlan brief ===
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Fa0/1, Fa0/2, Fa0/3, Fa0/4
10   Engineering                      active    Fa0/5, Fa0/6

=== Switch-2 show interfaces Fa0/10 switchport ===
Name: Fa0/10
Mode: access
Access Mode VLAN: 30 (inactive)`,
    source_ip: "192.168.10.10",
    dest_ip: "192.168.30.50",
    vlan_id: 30
  },
  {
    title: "PC1 default gateway mismatch",
    symptom: "Host PC1 cannot reach external internet or local router interface 192.168.1.1.",
    topology: "PC1 (192.168.1.50/24) -> Switch -> Router Fa0/0.1 (192.168.1.1/24)",
    concept: "Gateway",
    severity: "High",
    show_outputs: `=== PC1 Configuration ===
IP Address: 192.168.1.50
Subnet Mask: 255.255.255.0
Default Gateway: 192.168.2.1

=== Router Fa0/0.1 show ip interface brief ===
Fa0/0.1            192.168.1.1     YES manual up                    up`,
    source_ip: "192.168.1.50",
    gateway: "192.168.2.1",
    subnet_mask: "255.255.255.0"
  },
  {
    title: "Router subinterface administratively down",
    symptom: "All hosts in VLAN 15 lose connectivity to default gateway.",
    topology: "VLAN 15 Hosts -> Switch -> Router Gi0/0/0.15",
    concept: "Routing",
    severity: "Critical",
    show_outputs: `=== Router show ip interface brief ===
GigabitEthernet0/0/0.15   192.168.15.1   YES manual administratively down   down`,
    interface: "GigabitEthernet0/0/0.15"
  }
];

export default function NewCase({ setActivePage, setSelectedCaseId }) {
  const [title, setTitle] = useState('');
  const [symptom, setSymptom] = useState('');
  const [topology, setTopology] = useState('');
  const [showOutputs, setShowOutputs] = useState('');
  const [severity, setSeverity] = useState('Medium');
  const [concept, setConcept] = useState('Routing');
  
  // Device checklist state
  const [selectedDevices, setSelectedDevices] = useState(['PC', 'Switch', 'Router']);

  // Optional structured parameters
  const [sourceIp, setSourceIp] = useState('');
  const [destIp, setDestIp] = useState('');
  const [subnetMask, setSubnetMask] = useState('');
  const [gateway, setGateway] = useState('');
  const [vlanId, setVlanId] = useState('');
  const [interfaceName, setInterfaceName] = useState('');

  const [loading, setLoading] = useState(false);

  const availableDevices = ['PC', 'Switch', 'Router', 'Server', 'Access Point', 'Wireless Controller'];

  const toggleDevice = (device) => {
    if (selectedDevices.includes(device)) {
      setSelectedDevices(selectedDevices.filter(d => d !== device));
    } else {
      setSelectedDevices([...selectedDevices, device]);
    }
  };

  const applyTemplate = (tpl) => {
    setTitle(tpl.title);
    setSymptom(tpl.symptom);
    setTopology(tpl.topology);
    setConcept(tpl.concept);
    setSeverity(tpl.severity);
    setShowOutputs(tpl.show_outputs);
    if (tpl.source_ip) setSourceIp(tpl.source_ip);
    if (tpl.dest_ip) setDestIp(tpl.dest_ip);
    if (tpl.gateway) setGateway(tpl.gateway);
    if (tpl.subnet_mask) setSubnetMask(tpl.subnet_mask);
    if (tpl.vlan_id) setVlanId(tpl.vlan_id.toString());
    if (tpl.interface) setInterfaceName(tpl.interface);
  };

  const appendCommandSnippet = (commandText) => {
    setShowOutputs(prev => prev ? `${prev}\n\n=== ${commandText} ===\n` : `=== ${commandText} ===\n`);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim() || !symptom.trim() || !showOutputs.trim()) {
      alert('Please fill out Case Title, Symptom, and Show Command Outputs.');
      return;
    }

    setLoading(true);
    try {
      const caseData = {
        title,
        symptom,
        topology: topology || selectedDevices.join(' -> '),
        show_outputs: showOutputs,
        severity,
        concept,
        source_ip: sourceIp || null,
        dest_ip: destIp || null,
        subnet_mask: subnetMask || null,
        gateway: gateway || null,
        vlan_id: vlanId ? parseInt(vlanId) : null,
        interface: interfaceName || null,
        device: selectedDevices.join(', ')
      };

      const created = await createCase(caseData);
      
      // Automatically trigger rule check + AI diagnosis
      await diagnoseCase(created.id);

      setSelectedCaseId(created.id);
      setActivePage('case-detail');
    } catch (err) {
      console.error('Failed to create and diagnose case', err);
      alert('Error creating troubleshooting case.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      <div>
        <h2 style={{ fontSize: '1.5rem', fontWeight: '700', color: '#f8fafc' }}>
          New Network Troubleshooting Case
        </h2>
        <p style={{ fontSize: '0.875rem', color: '#94a3b8' }}>
          Submit Packet Tracer scenario evidence, Cisco CLI command outputs, and network topology for AI diagnosis.
        </p>
      </div>

      {/* Preset Quick Fill Templates */}
      <div className="glass-card" style={{ background: 'rgba(6, 182, 212, 0.05)', border: '1px dashed rgba(6, 182, 212, 0.3)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
          <Sparkles size={16} color="#06b6d4" />
          <span style={{ fontSize: '0.85rem', fontWeight: '700', color: '#06b6d4' }}>Quick Fill Preset Scenarios</span>
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
          {SAMPLE_TEMPLATES.map((tpl, idx) => (
            <button
              key={idx}
              type="button"
              className="btn btn-secondary"
              onClick={() => applyTemplate(tpl)}
              style={{ fontSize: '0.75rem', padding: '0.35rem 0.75rem' }}
            >
              Load: {tpl.title}
            </button>
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        
        {/* Case Title */}
        <div className="glass-card">
          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '700', marginBottom: '0.5rem', color: '#cbd5e1' }}>
            Case Title *
          </label>
          <input
            type="text"
            className="input-field"
            placeholder="e.g. PC cannot access server in VLAN 30"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </div>

        {/* Symptom & Topology */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1rem' }}>
          <div className="glass-card">
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '700', marginBottom: '0.5rem', color: '#cbd5e1' }}>
              Network Symptom *
            </label>
            <textarea
              className="textarea-field"
              placeholder="Describe the exact network issue (e.g. PC in VLAN 10 cannot ping server in VLAN 30...)"
              value={symptom}
              onChange={(e) => setSymptom(e.target.value)}
              required
            />
          </div>

          <div className="glass-card">
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '700', marginBottom: '0.5rem', color: '#cbd5e1' }}>
              Topology Notes
            </label>
            <textarea
              className="textarea-field"
              placeholder="e.g. PC-1 (192.168.10.10) -> Switch-1 -> Switch-2 -> Server-1 (192.168.30.50)"
              value={topology}
              onChange={(e) => setTopology(e.target.value)}
            />
          </div>
        </div>

        {/* Device Information Selector */}
        <div className="glass-card">
          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '700', marginBottom: '0.5rem', color: '#cbd5e1' }}>
            Involved Devices
          </label>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {availableDevices.map(dev => {
              const isSelected = selectedDevices.includes(dev);
              return (
                <button
                  key={dev}
                  type="button"
                  onClick={() => toggleDevice(dev)}
                  style={{
                    padding: '0.4rem 0.75rem',
                    borderRadius: '0.375rem',
                    fontSize: '0.8rem',
                    fontWeight: '600',
                    cursor: 'pointer',
                    background: isSelected ? 'rgba(6, 182, 212, 0.2)' : '#0f172a',
                    color: isSelected ? '#06b6d4' : '#64748b',
                    border: isSelected ? '1px solid #06b6d4' : '1px solid #1e293b'
                  }}
                >
                  {isSelected ? '✓ ' : '+ '}{dev}
                </button>
              );
            })}
          </div>
        </div>

        {/* Cisco Show Command Outputs */}
        <div className="glass-card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
            <label style={{ fontSize: '0.85rem', fontWeight: '700', color: '#cbd5e1', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Terminal size={16} color="#06b6d4" />
              <span>Cisco `show` Command Outputs *</span>
            </label>
            
            {/* Command Snippet Buttons */}
            <div style={{ display: 'flex', gap: '0.25rem' }}>
              {['show ip route', 'show vlan brief', 'show interfaces trunk', 'show access-lists', 'show ip interface brief'].map(cmd => (
                <button
                  key={cmd}
                  type="button"
                  onClick={() => appendCommandSnippet(cmd)}
                  style={{ fontSize: '0.7rem', padding: '0.2rem 0.5rem', background: '#0f172a', border: '1px solid #334155', color: '#94a3b8', borderRadius: '0.25rem', cursor: 'pointer' }}
                >
                  + {cmd}
                </button>
              ))}
            </div>
          </div>

          <textarea
            className="textarea-field"
            style={{ minHeight: '180px', color: '#a7f3d0' }}
            placeholder="Paste show command outputs (e.g. show ip route, show vlan brief, show ip interface brief)..."
            value={showOutputs}
            onChange={(e) => setShowOutputs(e.target.value)}
            required
          />
        </div>

        {/* Optional Structured Network Parameters */}
        <div className="glass-card">
          <h4 style={{ fontSize: '0.85rem', fontWeight: '700', color: '#cbd5e1', marginBottom: '0.75rem' }}>
            Optional Structured Network Information (Improves Rule Checking Precision)
          </h4>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.75rem' }}>
            <div>
              <label style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Source IP</label>
              <input type="text" className="input-field" placeholder="192.168.10.10" value={sourceIp} onChange={e => setSourceIp(e.target.value)} />
            </div>
            <div>
              <label style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Destination IP</label>
              <input type="text" className="input-field" placeholder="192.168.30.50" value={destIp} onChange={e => setDestIp(e.target.value)} />
            </div>
            <div>
              <label style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Subnet Mask</label>
              <input type="text" className="input-field" placeholder="255.255.255.0" value={subnetMask} onChange={e => setSubnetMask(e.target.value)} />
            </div>
            <div>
              <label style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Default Gateway</label>
              <input type="text" className="input-field" placeholder="192.168.10.1" value={gateway} onChange={e => setGateway(e.target.value)} />
            </div>
            <div>
              <label style={{ fontSize: '0.75rem', color: '#94a3b8' }}>VLAN ID</label>
              <input type="number" className="input-field" placeholder="30" value={vlanId} onChange={e => setVlanId(e.target.value)} />
            </div>
            <div>
              <label style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Interface</label>
              <input type="text" className="input-field" placeholder="Fa0/10" value={interfaceName} onChange={e => setInterfaceName(e.target.value)} />
            </div>
          </div>
        </div>

        {/* Severity & Concept Selection */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <div className="glass-card">
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '700', marginBottom: '0.5rem', color: '#cbd5e1' }}>
              Fault Concept
            </label>
            <select className="select-field" value={concept} onChange={e => setConcept(e.target.value)}>
              {['VLAN', 'Gateway', 'DHCP', 'DNS', 'Routing', 'ACL', 'NAT', 'Wireless', 'Other'].map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          <div className="glass-card">
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '700', marginBottom: '0.5rem', color: '#cbd5e1' }}>
              Severity Level
            </label>
            <select className="select-field" value={severity} onChange={e => setSeverity(e.target.value)}>
              {['Low', 'Medium', 'High', 'Critical'].map(s => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          className="btn btn-primary"
          disabled={loading}
          style={{ padding: '0.85rem', fontSize: '1rem', width: '100%', marginTop: '0.5rem' }}
        >
          {loading ? (
            <span>Running Deterministic Rules & AI Diagnosis...</span>
          ) : (
            <>
              <Send size={18} />
              <span>Run Troubleshooting Engine</span>
            </>
          )}
        </button>

      </form>
    </div>
  );
}
