import React, { useState, useEffect } from 'react';
import { Settings as SettingsIcon, Cpu, Database, Key, Server, RefreshCw } from 'lucide-react';
import { getSystemStatus } from '../services/api';

export default function Settings() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getSystemStatus().then(data => {
      setStatus(data);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      <div>
        <h2 style={{ fontSize: '1.5rem', fontWeight: '700', color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <SettingsIcon size={24} color="#06b6d4" />
          <span>System Settings & AI Engine Configuration</span>
        </h2>
        <p style={{ fontSize: '0.875rem', color: '#94a3b8' }}>
          Manage AI diagnosis provider settings, local demo mode fallbacks, and database status.
        </p>
      </div>

      <div className="glass-card">
        <h3 style={{ fontSize: '1rem', fontWeight: '700', color: '#f1f5f9', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Cpu size={18} color="#06b6d4" />
          <span>AI Engine Provider Mode</span>
        </h3>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <div style={{ background: '#0f172a', padding: '1rem', borderRadius: '0.5rem', border: '1px solid #1e293b', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <div style={{ fontWeight: '700', color: '#f1f5f9' }}>Active Mode: {status?.ai_mode || 'Mock AI Engine (Demo Mode)'}</div>
              <p style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '0.25rem' }}>
                {status?.ai_mode === 'Live API' 
                  ? 'Connected to live AI provider API via AI_API_KEY environment variable.'
                  : 'Operating in local Demo Mode with deterministic AI engine fallback (no external API key required).'}
              </p>
            </div>
            <span className="badge badge-ai">
              {status?.ai_mode || 'Mock Mode'}
            </span>
          </div>

          <div style={{ fontSize: '0.85rem', color: '#cbd5e1', lineHeight: '1.6' }}>
            <p><strong>To enable Live OpenAI/Gemini API:</strong></p>
            <code style={{ background: '#030712', padding: '0.35rem 0.6rem', borderRadius: '0.25rem', color: '#06b6d4', display: 'inline-block', marginTop: '0.25rem' }}>
              set AI_API_KEY=your_api_key_here
            </code>
          </div>
        </div>
      </div>

      <div className="glass-card">
        <h3 style={{ fontSize: '1rem', fontWeight: '700', color: '#f1f5f9', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Database size={18} color="#10b981" />
          <span>Database & Environment Info</span>
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', fontSize: '0.85rem' }}>
          <div style={{ background: '#0f172a', padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #1e293b' }}>
            <span style={{ color: '#94a3b8' }}>Backend Version</span>
            <div style={{ fontWeight: '700', color: '#f1f5f9', marginTop: '0.25rem' }}>{status?.version || '1.0.0'}</div>
          </div>
          <div style={{ background: '#0f172a', padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #1e293b' }}>
            <span style={{ color: '#94a3b8' }}>Database Dialect</span>
            <div style={{ fontWeight: '700', color: '#f1f5f9', marginTop: '0.25rem' }}>SQLite / PostgreSQL (SQLAlchemy)</div>
          </div>
        </div>
      </div>

    </div>
  );
}
