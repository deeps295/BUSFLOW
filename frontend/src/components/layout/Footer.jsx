import React from 'react';
import { MapPin, Cpu, ShieldCheck } from 'lucide-react';

export const Footer = () => {
  return (
    <footer className="mt-auto border-t border-white/5 bg-slate-950/60 backdrop-blur-md py-6 px-4 text-xs text-slate-400">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <MapPin className="w-4 h-4 text-brand-cyan" />
          <span>Sri Eshwar College of Engineering, Kondampatti, Kinathukadavu, Coimbatore – 641 202</span>
        </div>
        <div className="flex items-center gap-4 text-slate-500">
          <span className="flex items-center gap-1">
            <Cpu className="w-3.5 h-3.5 text-brand-emerald" />
            Supervised Regression Engine
          </span>
          <span>•</span>
          <span className="flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5 text-brand-cyan" />
            Official Transport Network
          </span>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
