import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Compass, Home, ArrowLeft } from 'lucide-react';
import { GlassPanel } from '../components/common/GlassWrappers';

export const NotFoundPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-[60vh] flex items-center justify-center p-6">
      <GlassPanel className="p-10 rounded-2xl border border-white/10 text-center max-w-md w-full space-y-5 bg-gradient-to-b from-surface-container to-surface-container-high shadow-2xl">
        <div className="w-16 h-16 rounded-2xl bg-primary-container/20 border border-primary-container/40 flex items-center justify-center text-primary-container mx-auto shadow-glow-critical">
          <Compass className="w-8 h-8 animate-spin-slow" />
        </div>

        <div className="space-y-2">
          <span className="font-mono text-3xl font-extrabold text-primary tracking-wider">
            404
          </span>
          <h1 className="text-xl font-bold text-white tracking-tight">
            Route Destination Not Found
          </h1>
          <p className="text-xs text-on-surface-variant leading-relaxed">
            The requested Cisco telemetry endpoint or dashboard route is not routed in the active routing table.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
          <button
            onClick={() => navigate(-1)}
            className="w-full sm:w-auto px-4 py-2 rounded-lg text-xs font-semibold bg-white/10 hover:bg-white/15 text-white border border-white/10 flex items-center justify-center gap-2 transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Go Back</span>
          </button>

          <button
            onClick={() => navigate('/')}
            className="w-full sm:w-auto px-4 py-2 rounded-lg text-xs font-bold bg-primary-container hover:bg-orange-500 text-white shadow-glow-critical flex items-center justify-center gap-2 transition-all active:scale-95"
          >
            <Home className="w-3.5 h-3.5" />
            <span>Dashboard</span>
          </button>
        </div>
      </GlassPanel>
    </div>
  );
};
