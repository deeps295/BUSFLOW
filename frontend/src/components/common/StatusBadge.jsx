import React from 'react';

/**
 * StatusBadge for delay severity, traffic conditions, and model statuses
 */
export const StatusBadge = ({ status, variant, label, className = '' }) => {
  const getStyle = () => {
    const key = (variant || status || '').toLowerCase();
    switch (key) {
      case 'on_time':
      case 'low':
      case 'active':
      case 'success':
      case 'completed':
        return 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30';
      case 'minor_delay':
      case 'medium':
      case 'in_progress':
      case 'scheduled':
        return 'bg-amber-500/15 text-amber-300 border-amber-500/30';
      case 'moderate_delay':
      case 'high':
      case 'warning':
        return 'bg-orange-500/15 text-orange-300 border-orange-500/30';
      case 'severe_delay':
      case 'severe':
      case 'critical':
      case 'cancelled':
        return 'bg-rose-500/15 text-rose-300 border-rose-500/30';
      case 'synthetic':
        return 'bg-purple-500/15 text-purple-300 border-purple-500/30';
      case 'info':
      default:
        return 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30';
    }
  };

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border ${getStyle()} ${className}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />
      {label || status}
    </span>
  );
};

export default StatusBadge;
