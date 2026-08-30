import React, { createContext, useContext, useState, useCallback } from 'react';
import { CheckCircle2, AlertTriangle, XCircle, Info, X } from 'lucide-react';
import { AnimatePresence, motion } from 'framer-motion';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface ToastItem {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
}

interface ToastContextValue {
  showToast: (type: ToastType, title: string, message?: string) => void;
}

const ToastContext = createContext<ToastContextValue | undefined>(undefined);

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const showToast = useCallback((type: ToastType, title: string, message?: string) => {
    const id = `toast-${Date.now()}-${Math.random()}`;
    const newToast: ToastItem = { id, type, title, message };
    setToasts(prev => [...prev, newToast]);

    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 4500);
  }, []);

  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      {/* Toast Accessibility Container with aria-live */}
      <div
        className="fixed top-5 right-5 z-50 flex flex-col gap-2 pointer-events-none max-w-md w-full"
        aria-live="polite"
        aria-atomic="false"
        role="region"
        aria-label="System Notifications"
      >
        <AnimatePresence>
          {toasts.map(toast => {
            const icons = {
              success: <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />,
              warning: <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0" />,
              error: <XCircle className="w-5 h-5 text-red-400 shrink-0" />,
              info: <Info className="w-5 h-5 text-secondary shrink-0" />,
            };

            const borderColors = {
              success: 'border-emerald-500/40 shadow-glow-emerald',
              warning: 'border-amber-500/40 shadow-glow-warning',
              error: 'border-red-500/40',
              info: 'border-secondary/40 shadow-glow-cyan',
            };

            return (
              <motion.div
                key={toast.id}
                role="status"
                initial={{ opacity: 0, y: -20, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9, transition: { duration: 0.2 } }}
                className={`pointer-events-auto glass-panel p-4 rounded-xl border flex items-start gap-3 shadow-2xl ${borderColors[toast.type]}`}
              >
                {icons[toast.type]}
                <div className="flex-1 min-w-0">
                  <h4 className="text-sm font-semibold text-white tracking-wide">{toast.title}</h4>
                  {toast.message && (
                    <p className="text-xs text-on-surface-variant mt-0.5 leading-relaxed">{toast.message}</p>
                  )}
                </div>
                <button
                  onClick={() => removeToast(toast.id)}
                  className="text-on-surface-variant hover:text-white transition-colors p-1"
                  aria-label="Dismiss notification"
                  title="Dismiss notification"
                >
                  <X className="w-4 h-4" />
                </button>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
};

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) throw new Error('useToast must be used within a ToastProvider');
  return context;
};
