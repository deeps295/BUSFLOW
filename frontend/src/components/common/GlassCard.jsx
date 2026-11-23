import React from 'react';

/**
 * Reusable Glassmorphism Card
 * @param {boolean} interactive - whether card has hover elevation and glow
 * @param {string} className - extra Tailwind classes
 */
export const GlassCard = ({ children, interactive = false, className = '', ...props }) => {
  const baseClass = interactive ? 'glass-card-interactive' : 'glass-card';
  return (
    <div className={`${baseClass} rounded-2xl p-6 ${className}`} {...props}>
      {children}
    </div>
  );
};

export default GlassCard;
