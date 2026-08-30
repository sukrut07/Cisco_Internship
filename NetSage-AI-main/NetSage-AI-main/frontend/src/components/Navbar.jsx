import React from 'react';
import { 
  Activity, 
  PlusCircle, 
  FolderCheck, 
  Cpu, 
  ShieldCheck, 
  CheckCircle2, 
  Settings,
  Terminal
} from 'lucide-react';

export default function Navbar({ activePage, setActivePage, aiStatus }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Activity },
    { id: 'new-case', label: 'New Case', icon: PlusCircle },
    { id: 'cases', label: 'Cases Directory', icon: FolderCheck },
    { id: 'rule-checker', label: 'Rule Checker', icon: Cpu },
    { id: 'responsible-ai', label: 'Responsible AI', icon: ShieldCheck },
    { id: 'verification', label: 'Fix Verification', icon: CheckCircle2 },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <header style={{ background: '#0d1527', borderBottom: '1px solid #1e293b' }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '0.75rem 1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        
        {/* Brand Logo */}
        <div 
          onClick={() => setActivePage('dashboard')}
          style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', cursor: 'pointer' }}
        >
          <div style={{ background: 'linear-gradient(135deg, #06b6d4, #3b82f6)', padding: '0.5rem', borderRadius: '0.5rem', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Terminal size={22} color="#ffffff" />
          </div>
          <div>
            <h1 style={{ fontSize: '1.25rem', fontWeight: '700', letterSpacing: '-0.025em', background: 'linear-gradient(to right, #06b6d4, #60a5fa)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              NetSage AI
            </h1>
            <p style={{ fontSize: '0.7rem', color: '#64748b', fontWeight: '500' }}>
              Cisco Network Troubleshooting Assistant
            </p>
          </div>
        </div>

        {/* Navigation Items */}
        <nav style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activePage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActivePage(item.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  padding: '0.5rem 0.85rem',
                  borderRadius: '0.375rem',
                  fontSize: '0.85rem',
                  fontWeight: '600',
                  color: isActive ? '#06b6d4' : '#94a3b8',
                  background: isActive ? 'rgba(6, 182, 212, 0.12)' : 'transparent',
                  border: isActive ? '1px solid rgba(6, 182, 212, 0.3)' : '1px solid transparent',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
              >
                <Icon size={16} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* System & AI Mode Indicator */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div className="badge badge-ai" style={{ padding: '0.35rem 0.75rem' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#06b6d4', display: 'inline-block' }}></span>
            <span>{aiStatus?.ai_mode || 'Mock AI Engine'}</span>
          </div>
        </div>

      </div>
    </header>
  );
}
