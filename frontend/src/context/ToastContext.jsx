import React, { createContext, useContext, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, AlertTriangle, Info, X } from 'lucide-react';

const ToastContext = createContext(null);

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((message, type = 'success', durationMs = 4000) => {
    const id = Date.now() + Math.random().toString(36).substring(2, 6);
    setToasts((prev) => [...prev, { id, message, type }]);

    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, durationMs);
  }, []);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const showToast = useCallback((message, type = 'success', durationMs = 4000) => {
    addToast(message, type, durationMs);
  }, [addToast]);

  return (
    <ToastContext.Provider value={{ addToast, showToast }}>
      {children}
      {/* Toast Render Portal */}
      <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none px-4">
        <AnimatePresence>
          {toasts.map((t) => (
            <motion.div
              key={t.id}
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 10, scale: 0.95 }}
              transition={{ duration: 0.2 }}
              className={`pointer-events-auto flex items-center justify-between p-3.5 rounded-xl border backdrop-blur-xl shadow-xl text-xs font-medium ${
                t.type === 'error'
                  ? 'bg-rose-950/80 border-rose-500/30 text-rose-200 shadow-rose-900/20'
                  : t.type === 'warning'
                  ? 'bg-amber-950/80 border-amber-500/30 text-amber-200 shadow-amber-900/20'
                  : 'bg-emerald-950/80 border-emerald-500/30 text-emerald-200 shadow-emerald-900/20'
              }`}
            >
              <div className="flex items-center gap-2.5">
                {t.type === 'error' ? (
                  <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
                ) : t.type === 'warning' ? (
                  <Info className="w-4 h-4 text-amber-400 shrink-0" />
                ) : (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                )}
                <span>{t.message}</span>
              </div>
              <button
                onClick={() => removeToast(t.id)}
                className="text-white/40 hover:text-white p-1 rounded-md transition-colors"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
};

export const useToast = () => useContext(ToastContext);
export default ToastContext;
