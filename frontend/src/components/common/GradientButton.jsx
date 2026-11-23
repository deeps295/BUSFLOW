import React from 'react';
import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';

const GradientButton = ({
  children,
  onClick,
  disabled = false,
  loading = false,
  className = '',
  type = 'button',
}) => {
  return (
    <motion.button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      whileTap={{ scale: 0.97 }}
      whileHover={{ scale: 1.02 }}
      className={`
        relative flex items-center justify-center gap-2 font-semibold py-3 px-6 rounded-xl
        bg-gradient-to-r from-blue-600 to-teal-500
        hover:from-blue-500 hover:to-teal-400
        disabled:from-blue-900 disabled:to-teal-900 disabled:cursor-not-allowed disabled:opacity-60
        text-white transition-all shadow-lg shadow-blue-900/30
        ${className}
      `}
    >
      {loading && <Loader2 className="w-4 h-4 animate-spin" />}
      {children}
    </motion.button>
  );
};

export default GradientButton;
