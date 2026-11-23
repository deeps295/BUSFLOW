import React from 'react';
import { motion } from 'framer-motion';

const MetricCard = ({ icon: Icon, label, value, sub, color = 'text-sky-400' }) => {
  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-5 flex items-start gap-4"
    >
      {Icon && (
        <div className={`w-11 h-11 rounded-xl flex items-center justify-center bg-white/10 flex-shrink-0`}>
          <Icon className={`w-5 h-5 ${color}`} />
        </div>
      )}
      <div className="min-w-0">
        <p className="text-white/50 text-xs font-medium uppercase tracking-wider mb-1">{label}</p>
        <p className="text-white text-2xl font-bold leading-none mb-1">{value}</p>
        {sub && <p className="text-white/40 text-xs">{sub}</p>}
      </div>
    </motion.div>
  );
};

export default MetricCard;
