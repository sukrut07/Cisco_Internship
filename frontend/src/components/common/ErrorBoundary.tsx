import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertOctagon, RotateCcw, Home } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallbackTitle?: string;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error, errorInfo: null };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({ error, errorInfo });
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-[400px] flex items-center justify-center p-6 w-full">
          <div className="glass-panel p-8 rounded-2xl border border-red-500/40 shadow-2xl max-w-xl w-full text-center space-y-4 bg-gradient-to-b from-red-950/20 to-surface-container">
            <div className="w-14 h-14 rounded-2xl bg-red-500/20 border border-red-500/40 flex items-center justify-center text-red-400 mx-auto shadow-lg">
              <AlertOctagon className="w-7 h-7" />
            </div>

            <div className="space-y-1">
              <h2 className="text-xl font-bold text-white tracking-tight">
                {this.props.fallbackTitle || 'Component Rendering Exception'}
              </h2>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                An unexpected exception was caught by the NetSage Error Boundary. The system safely prevented a crash.
              </p>
            </div>

            {this.state.error && (
              <div className="bg-black/50 p-3 rounded-lg border border-white/10 text-left font-mono text-xs text-red-300 max-h-36 overflow-y-auto">
                <p className="font-bold">{this.state.error.name}: {this.state.error.message}</p>
                {this.state.errorInfo?.componentStack && (
                  <pre className="text-[10px] text-outline mt-1 whitespace-pre-wrap">
                    {this.state.errorInfo.componentStack}
                  </pre>
                )}
              </div>
            )}

            <div className="flex items-center justify-center gap-3 pt-2">
              <button
                onClick={this.handleReset}
                className="px-4 py-2 rounded-lg text-xs font-bold font-sans bg-primary-container hover:bg-orange-500 text-white shadow-glow-critical flex items-center gap-2 transition-all active:scale-95"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Reload Application</span>
              </button>

              <a
                href="/"
                className="px-4 py-2 rounded-lg text-xs font-semibold font-sans bg-white/10 hover:bg-white/15 text-white border border-white/10 flex items-center gap-2 transition-colors"
              >
                <Home className="w-3.5 h-3.5" />
                <span>Return to Dashboard</span>
              </a>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
