import React from 'react';
import GlassCard from '../components/common/GlassCard';
import StatusBadge from '../components/common/StatusBadge';
import { 
  Bus, 
  MapPin, 
  Clock, 
  Cpu, 
  CheckCircle2, 
  ArrowRight, 
  Sparkles,
  Layers,
  Activity,
  Compass,
  Gauge,
  ShieldCheck,
  Database
} from 'lucide-react';

export const HomePage = ({ healthData, isConnected, onSelectTab }) => {
  return (
    <div className="space-y-10">
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-3xl p-8 sm:p-12 glass-card border border-white/10">
        <div className="max-w-3xl space-y-5">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            Machine Learning Powered Arrival Analytics
          </div>

          <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white leading-tight">
            Next-Gen Bus Arrival & Delay Prediction for{' '}
            <span className="bg-gradient-to-r from-sky-400 via-cyan-300 to-emerald-400 bg-clip-text text-transparent">
              Sri Eshwar College of Engineering
            </span>
          </h1>

          <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
            Eliminating morning commute uncertainty across Coimbatore and Pollachi. 
            Powered by real-time traffic updates, historical segment analytics, Open-Meteo weather synthesis, 
            and genuine supervised regression models.
          </p>

          <div className="flex flex-wrap gap-3 pt-2">
            <button 
              onClick={() => onSelectTab && onSelectTab('student')}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-teal-500 hover:from-cyan-400 hover:to-teal-400 text-slate-950 font-bold text-xs sm:text-sm shadow-lg shadow-cyan-500/25 transition-all hover:scale-[1.02] active:scale-[0.98]"
            >
              <Compass className="w-4 h-4" />
              Track My College Bus
              <ArrowRight className="w-4 h-4" />
            </button>

            <button 
              onClick={() => onSelectTab && onSelectTab('driver')}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 text-white font-semibold text-xs sm:text-sm border border-white/10 transition-all hover:scale-[1.02]"
            >
              <Gauge className="w-4 h-4 text-cyan-400" />
              Driver Live Cockpit
            </button>
          </div>
        </div>
      </div>

      {/* System Status Indicators */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <GlassCard className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Backend API</span>
            <StatusBadge status={isConnected ? "Active" : "Connecting"} variant={isConnected ? "active" : "minor_delay"} />
          </div>
          <div className="text-xl font-bold text-white flex items-center gap-2">
            <Activity className="w-5 h-5 text-cyan-400" />
            {isConnected ? "FastAPI Core Online" : "Connecting..."}
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            {healthData ? (
              <>Version {healthData.version} • SQLite DB {healthData.database} • {healthData.institution?.name}</>
            ) : (
              <>FastAPI server expected on http://127.0.0.1:8000.</>
            )}
          </p>
        </GlassCard>

        <GlassCard className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Database Schema</span>
            <StatusBadge status="11 Tables Created" variant="success" />
          </div>
          <div className="text-xl font-bold text-white flex items-center gap-2">
            <Database className="w-5 h-5 text-emerald-400" />
            SQLite Relational Core
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Users, Buses, Drivers, Students, Routes, Stops, Schedules, Trips, TripSegments, TrafficReports, ModelTrainingHistory.
          </p>
        </GlassCard>

        <GlassCard className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Transport Network</span>
            <StatusBadge status="SECE Coimbatore" variant="success" />
          </div>
          <div className="text-xl font-bold text-white flex items-center gap-2">
            <MapPin className="w-5 h-5 text-teal-400" />
            5 Key Corridors
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Kanuvai (Rt 45), Palladam (Rt 40), Postal Colony (Rt 42), Saravanampatti (Rt 3), Pollachi (Rt 46).
          </p>
        </GlassCard>
      </div>

      {/* Role Portals */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Layers className="w-5 h-5 text-brand-cyan" />
            SECE BusFlow Roles & Portals
          </h2>
          <span className="text-xs text-slate-400">Phase 1 Foundation Setup</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Student Portal Card */}
          <GlassCard 
            interactive 
            onClick={() => onSelectTab && onSelectTab('student')}
            className="cursor-pointer space-y-4 group"
          >
            <div className="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 group-hover:scale-110 transition-transform">
              <Compass className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white group-hover:text-cyan-300 transition-colors">
                1. Student Arrival Portal
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                Select your SECE bus route & boarding stop. View predicted arrival countdown, delay minutes, and real-time Leaflet route tracking.
              </p>
            </div>
            <div className="pt-2 flex items-center text-xs font-semibold text-cyan-400 gap-1">
              Explore Student Dashboard <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </div>
          </GlassCard>

          {/* Driver Cockpit Card */}
          <GlassCard 
            interactive 
            onClick={() => onSelectTab && onSelectTab('driver')}
            className="cursor-pointer space-y-4 group"
          >
            <div className="w-12 h-12 rounded-xl bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400 group-hover:scale-110 transition-transform">
              <Gauge className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white group-hover:text-teal-300 transition-colors">
                2. Driver Live Cockpit
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                Assigned bus cockpit. Drivers toggle live traffic status (Low, Medium, High, Severe), report road issues, and log stop check-ins with one tap.
              </p>
            </div>
            <div className="pt-2 flex items-center text-xs font-semibold text-teal-400 gap-1">
              Explore Driver Cockpit <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </div>
          </GlassCard>

          {/* Admin Hub Card */}
          <GlassCard 
            interactive 
            onClick={() => onSelectTab && onSelectTab('admin')}
            className="cursor-pointer space-y-4 group"
          >
            <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 group-hover:scale-110 transition-transform">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white group-hover:text-emerald-300 transition-colors">
                3. Admin & ML Center
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                Fleet and route manager. Trigger model retraining, inspect MAE/RMSE benchmark charts, and monitor real vs synthetic training data ratios.
              </p>
            </div>
            <div className="pt-2 flex items-center text-xs font-semibold text-emerald-400 gap-1">
              Explore Admin & ML Center <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </div>
          </GlassCard>
        </div>
      </div>

      {/* Scaffolding Verification Banner */}
      <GlassCard className="border-cyan-500/20 bg-gradient-to-br from-slate-900/90 to-brand-navy/60">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              <h4 className="font-bold text-white text-sm sm:text-base">
                Phase 1 Scaffolding & Design Foundation Initialized
              </h4>
            </div>
            <p className="text-xs text-slate-400">
              Modular folder layout, React + Vite frontend, Tailwind CSS palette, 11 SQLAlchemy models, and FastAPI health check API are fully operational.
            </p>
          </div>
          <div className="flex items-center gap-2 text-xs font-mono bg-slate-950/80 px-3 py-1.5 rounded-lg border border-white/10 text-cyan-300">
            <span>Phase 1 Verification Complete</span>
          </div>
        </div>
      </GlassCard>
    </div>
  );
};

export default HomePage;
