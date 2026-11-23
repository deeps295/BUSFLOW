import React from 'react';
import { motion } from 'framer-motion';

const EmptyState = ({ icon: Icon, title = 'Nothing here yet', description = '' }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col items-center justify-center py-16 px-6 bg-white/5 border border-white/10 rounded-2xl text-center"
    >
      {Icon && (
        <div className="w-16 h-16 rounded-2xl bg-sky-500/15 flex items-center justify-center mb-5">
          <Icon className="w-8 h-8 text-sky-400" />
        </div>
      )}
      <p className="text-white font-semibold text-lg mb-2">{title}</p>
      {description && <p className="text-white/50 text-sm max-w-xs">{description}</p>}
    </motion.div>
  );
};

export default EmptyState;
