import React from 'react';
import { motion, useReducedMotion } from 'framer-motion';

/**
 * BubbleBackground
 * Premium, GPU-accelerated animated background using Framer Motion.
 * Features smooth, slow-floating ambient bubbles in cyan, teal, emerald, and royal blue.
 * Includes full respect for reduced-motion accessibility and non-blocking pointer events.
 */
export const BubbleBackground = () => {
  const shouldReduceMotion = useReducedMotion();

  // Distinct bubble configurations (size, position, colors, speeds)
  const bubbles = [
    {
      id: 1,
      size: 440,
      initial: { x: '-10%', y: '-10%', opacity: 0.28 },
      animate: shouldReduceMotion
        ? { opacity: 0.25 }
        : {
            x: ['-10%', '5%', '-5%', '-10%'],
            y: ['-10%', '15%', '5%', '-10%'],
            opacity: [0.22, 0.32, 0.22],
            scale: [1, 1.08, 0.98, 1],
          },
      duration: 22,
      gradient: 'radial-gradient(circle, #06B6D4 0%, #14B8A6 60%, transparent 100%)',
    },
    {
      id: 2,
      size: 520,
      initial: { x: '80%', y: '70%', opacity: 0.22 },
      animate: shouldReduceMotion
        ? { opacity: 0.2 }
        : {
            x: ['80%', '65%', '75%', '80%'],
            y: ['70%', '55%', '80%', '70%'],
            opacity: [0.18, 0.28, 0.18],
            scale: [1, 1.06, 0.96, 1],
          },
      duration: 26,
      gradient: 'radial-gradient(circle, #10B981 0%, #2563EB 70%, transparent 100%)',
    },
    {
      id: 3,
      size: 360,
      initial: { x: '75%', y: '10%', opacity: 0.25 },
      animate: shouldReduceMotion
        ? { opacity: 0.25 }
        : {
            x: ['75%', '60%', '70%', '75%'],
            y: ['10%', '25%', '5%', '10%'],
            opacity: [0.2, 0.3, 0.2],
            scale: [1, 1.1, 1],
          },
      duration: 18,
      gradient: 'radial-gradient(circle, #2563EB 0%, #38BDF8 60%, transparent 100%)',
    },
    {
      id: 4,
      size: 320,
      initial: { x: '15%', y: '65%', opacity: 0.24 },
      animate: shouldReduceMotion
        ? { opacity: 0.22 }
        : {
            x: ['15%', '25%', '10%', '15%'],
            y: ['65%', '50%', '70%', '65%'],
            opacity: [0.18, 0.3, 0.18],
            scale: [1, 1.08, 0.95, 1],
          },
      duration: 20,
      gradient: 'radial-gradient(circle, #14B8A6 0%, #06B6D4 70%, transparent 100%)',
    },
    {
      id: 5,
      size: 260,
      initial: { x: '45%', y: '35%', opacity: 0.16 },
      animate: shouldReduceMotion
        ? { opacity: 0.16 }
        : {
            x: ['45%', '52%', '40%', '45%'],
            y: ['35%', '42%', '30%', '35%'],
            opacity: [0.12, 0.22, 0.12],
            scale: [1, 1.12, 1],
          },
      duration: 16,
      gradient: 'radial-gradient(circle, #38BDF8 0%, #10B981 80%, transparent 100%)',
    },
  ];

  return (
    <div 
      className="fixed inset-0 pointer-events-none -z-10 overflow-hidden select-none"
      aria-hidden="true"
    >
      {/* Brand Base Gradient: Deep Navy Blue foundation with soft vignette */}
      <div 
        className="absolute inset-0"
        style={{
          background: 'radial-gradient(circle at 30% 20%, #0B1E3D 0%, #071B3A 50%, #030C1D 100%)'
        }}
      />

      {/* Animated Floating Bubbles */}
      {bubbles.map((b) => (
        <motion.div
          key={b.id}
          initial={b.initial}
          animate={b.animate}
          transition={{
            duration: b.duration,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          className="absolute rounded-full blur-3xl"
          style={{
            width: b.size,
            height: b.size,
            background: b.gradient,
            willChange: 'transform, opacity',
          }}
        />
      ))}

      {/* Subtle tech micro-grid pattern */}
      <div 
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: 'radial-gradient(#ffffff 1px, transparent 1px)',
          backgroundSize: '28px 28px',
        }}
      />
    </div>
  );
};

export default BubbleBackground;
