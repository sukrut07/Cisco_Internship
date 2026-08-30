import React, { useState } from 'react';
import { Copy, Check, Terminal } from 'lucide-react';

export default function CodeViewer({ title = 'Cisco CLI Show Output', code = '' }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="cli-box">
      <div className="cli-titlebar">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Terminal size={14} color="#06b6d4" />
          <span style={{ fontWeight: '600', color: '#cbd5e1' }}>{title}</span>
        </div>
        <button
          onClick={handleCopy}
          style={{
            background: 'transparent',
            border: 'none',
            color: copied ? '#10b981' : '#64748b',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '0.3rem',
            fontSize: '0.75rem'
          }}
        >
          {copied ? <Check size={14} /> : <Copy size={14} />}
          <span>{copied ? 'Copied' : 'Copy'}</span>
        </button>
      </div>
      <div className="cli-content">
        {code || '# No command output provided'}
      </div>
    </div>
  );
}
