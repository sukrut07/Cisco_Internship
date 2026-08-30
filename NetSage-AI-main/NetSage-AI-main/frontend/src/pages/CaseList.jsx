import React, { useState, useEffect } from 'react';
import { Search, Filter, FolderCheck, ArrowRight, RefreshCw } from 'lucide-react';
import { getCases } from '../services/api';

export default function CaseList({ setActivePage, setSelectedCaseId }) {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [conceptFilter, setConceptFilter] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');

  const fetchCasesData = async () => {
    setLoading(true);
    try {
      const data = await getCases({
        search: search || undefined,
        concept: conceptFilter || undefined,
        severity: severityFilter || undefined
      });
      setCases(data);
    } catch (err) {
      console.error('Failed to fetch cases', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCasesData();
  }, [search, conceptFilter, severityFilter]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* Page Title */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: '700', color: '#f8fafc' }}>
            Troubleshooting Cases Directory ({cases.length})
          </h2>
          <p style={{ fontSize: '0.875rem', color: '#94a3b8' }}>
            Browse and filter Cisco Packet Tracer troubleshooting lab cases.
          </p>
        </div>
        <button className="btn btn-primary" onClick={() => setActivePage('new-case')}>
          + New Case
        </button>
      </div>

      {/* Search and Filters Bar */}
      <div className="glass-card" style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', alignItems: 'center', justifyContent: 'space-between' }}>
        
        {/* Search Input */}
        <div style={{ flex: '1 1 300px', position: 'relative' }}>
          <Search size={16} color="#64748b" style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)' }} />
          <input
            type="text"
            className="input-field"
            style={{ paddingLeft: '2.25rem' }}
            placeholder="Search by Case ID, title, or symptom..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        {/* Filter Dropdowns */}
        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          <select 
            className="select-field" 
            style={{ width: '160px' }}
            value={conceptFilter}
            onChange={(e) => setConceptFilter(e.target.value)}
          >
            <option value="">All Concepts</option>
            {['VLAN', 'Gateway', 'DHCP', 'DNS', 'Routing', 'ACL', 'NAT', 'Wireless', 'Other'].map(c => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>

          <select 
            className="select-field" 
            style={{ width: '160px' }}
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
          >
            <option value="">All Severities</option>
            {['Low', 'Medium', 'High', 'Critical'].map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>

      </div>

      {/* Cases Directory Table */}
      <div className="glass-card">
        {loading ? (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '3rem' }}>
            <RefreshCw className="animate-spin" size={24} color="#06b6d4" />
            <span style={{ marginLeft: '0.5rem', color: '#94a3b8' }}>Fetching cases directory...</span>
          </div>
        ) : cases.length === 0 ? (
          <div style={{ padding: '3rem', textAlign: 'center', color: '#64748b' }}>
            No troubleshooting cases found matching search criteria.
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #1e293b', color: '#64748b' }}>
                  <th style={{ padding: '0.85rem' }}>Case ID</th>
                  <th style={{ padding: '0.85rem' }}>Title</th>
                  <th style={{ padding: '0.85rem' }}>Symptom Preview</th>
                  <th style={{ padding: '0.85rem' }}>Concept</th>
                  <th style={{ padding: '0.85rem' }}>Severity</th>
                  <th style={{ padding: '0.85rem' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {cases.map((c) => (
                  <tr key={c.id} style={{ borderBottom: '1px solid #131b2e' }}>
                    <td style={{ padding: '0.85rem', fontFamily: 'Fira Code', fontWeight: '700', color: '#06b6d4' }}>
                      {c.id}
                    </td>
                    <td style={{ padding: '0.85rem', fontWeight: '600', color: '#f1f5f9', maxWidth: '240px' }}>
                      {c.title}
                    </td>
                    <td style={{ padding: '0.85rem', color: '#94a3b8', maxWidth: '300px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {c.symptom}
                    </td>
                    <td style={{ padding: '0.85rem' }}>
                      <span className="badge badge-info">{c.concept}</span>
                    </td>
                    <td style={{ padding: '0.85rem' }}>
                      <span className={`badge ${c.severity === 'Critical' ? 'badge-fail' : c.severity === 'High' ? 'badge-warning' : 'badge-info'}`}>
                        {c.severity}
                      </span>
                    </td>
                    <td style={{ padding: '0.85rem' }}>
                      <button
                        className="btn btn-primary"
                        onClick={() => {
                          setSelectedCaseId(c.id);
                          setActivePage('case-detail');
                        }}
                        style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}
                      >
                        <span>Diagnose & Review</span>
                        <ArrowRight size={14} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

    </div>
  );
}
