import React from 'react';

const LoadingSkeleton = ({ className = '', lines = 3 }) => {
  return (
    <div className={`space-y-3 ${className}`}>
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="animate-pulse bg-white/10 rounded-xl"
          style={{ height: '1.25rem', width: i === lines - 1 ? '75%' : '100%' }}
        />
      ))}
    </div>
  );
};

export default LoadingSkeleton;
