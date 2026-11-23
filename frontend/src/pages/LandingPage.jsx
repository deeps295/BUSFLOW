import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Bus, MapPin, Brain, ArrowRight, Users, BarChart2, Clock } from 'lucide-react';
import BubbleBackground from '../components/layout/BubbleBackground';
import Navbar from '../components/layout/Navbar';
import { useAuth, DEMO_CREDENTIALS } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';

const SECE_ROUTES = [
  { id: '1', num: 'R01', name: 'Bharathiar University' },
  { id: '2', num: 'R02', name: 'Kottampatti–Pollachi' },
  { id: '3', num: 'R03', name: 'Saravanampatti' },
  { id: '4', num: 'R04', name: 'Kovaipudur' },
  { id: '5', num: 'R05', name: 'Vadakkipalayam' },
  { id: '6', num: 'R06', name: 'Sulur' },
  { id: '7', num: 'R07', name: 'Pollachi' },
  { id: '8', num: 'R08', name: 'Periyanaickenpalayam' },
  { id: '9', num: 'R09', name: 'Gandhipuram' },
  { id: '10', num: 'R10', name: 'Ukkadam' },
];

const STEPS = [
  { icon: MapPin, title: 'Select Route', desc: 'Choose your SECE bus route and boarding stop from the student portal.' },
  { icon: Brain, title: 'ML Prediction', desc: 'HistGradientBoosting model calculates arrival using 14 real-time features including traffic & weather.' },
  { icon: Bus, title: 'Board Confidently', desc: 'Get precise arrival time with ±2.3 min estimated prediction interval.' },
];

const DEMO_ROLES = [
  { key: 'ADMIN', label: 'Admin', icon: BarChart2, color: 'from-purple-600 to-purple-800', border: 'border-purple-500/30', dest: '/admin' },
  { key: 'DRIVER', label: 'Driver', icon: Bus, color: 'from-orange-600 to-orange-800', border: 'border-orange-500/30', dest: '/driver' },
  { key: 'STUDENT', label: 'Student', icon: Users, color: 'from-sky-600 to-sky-800', border: 'border-sky-500/30', dest: '/student' },
];

const container = { hidden: {}, show: { transition: { staggerChildren: 0.1 } } };
const item = { hidden: { opacity: 0, y: 24 }, show: { opacity: 1, y: 0 } };

export default function LandingPage() {
  const { quickDemoLogin } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();

  const handleDemo = async (roleKey, dest) => {
    try {
      await quickDemoLogin(roleKey);
      showToast(`Logged in as ${roleKey}`, 'success');
      navigate(dest);
    } catch {
      showToast('Demo login failed – is the backend running on port 8001?', 'error');
    }
  };

  return (
    <div className="min-h-screen relative overflow-x-hidden" style={{ background: 'linear-gradient(135deg, #071B3A 0%, #0F2D5E 50%, #071B3A 100%)' }}>
      <BubbleBackground />
      <div className="relative z-10">
        <Navbar />

        {/* ── HERO ── */}
        <section className="min-h-[90vh] flex flex-col items-center justify-center text-center px-4 py-20">
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.5 }}
            className="w-24 h-24 rounded-3xl bg-gradient-to-br from-blue-600 to-teal-500 flex items-center justify-center mb-8 shadow-2xl shadow-blue-900/50 mx-auto"
          >
            <Bus className="w-12 h-12 text-white" />
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
            className="text-6xl sm:text-7xl font-black text-transparent bg-clip-text bg-gradient-to-r from-sky-400 via-cyan-400 to-teal-400 mb-4"
          >
            BusFlow
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
            className="text-sky-300 text-xl sm:text-2xl font-semibold mb-4"
          >
            Smart Arrival. Less Waiting.
          </motion.p>

          <motion.p
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
            className="text-white/50 text-base sm:text-lg max-w-xl mb-10"
          >
            AI-powered bus arrival predictions for Sri Eshwar College of Engineering, Coimbatore.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
            className="flex flex-wrap gap-4 justify-center mb-16"
          >
            <Link to="/student"
              className="flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-blue-600 to-teal-500 hover:from-blue-500 hover:to-teal-400 text-white font-semibold rounded-2xl shadow-xl shadow-blue-900/40 transition-all"
            >
              <Bus className="w-5 h-5" /> Track My Bus <ArrowRight className="w-4 h-4" />
            </Link>
            <Link to="/login"
              className="flex items-center gap-2 px-8 py-4 bg-white/5 hover:bg-white/10 border border-white/20 text-white font-semibold rounded-2xl transition-all"
            >
              Driver Login
            </Link>
          </motion.div>

          {/* Stats */}
          <motion.div variants={container} initial="hidden" animate="show"
            className="grid grid-cols-3 gap-4 max-w-sm mx-auto">
            {[['10', 'Routes'], ['88', 'Stops'], ['1.64 min', 'Test MAE']].map(([val, label]) => (
              <motion.div key={label} variants={item}
                className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl px-4 py-5 text-center">
                <p className="text-white text-xl font-black">{val}</p>
                <p className="text-white/40 text-xs mt-1">{label}</p>
              </motion.div>
            ))}
          </motion.div>
        </section>

        {/* ── HOW IT WORKS ── */}
        <section className="py-20 px-4 max-w-5xl mx-auto">
          <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
            className="text-center mb-14">
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">How It Works</h2>
            <div className="w-16 h-1 bg-gradient-to-r from-blue-600 to-teal-500 rounded-full mx-auto" />
          </motion.div>
          <motion.div variants={container} initial="hidden" whileInView="show" viewport={{ once: true }}
            className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {STEPS.map((step, i) => (
              <motion.div key={step.title} variants={item}
                className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-7 text-center">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-600 to-teal-500 flex items-center justify-center mx-auto mb-5 shadow-lg shadow-blue-900/40">
                  <step.icon className="w-7 h-7 text-white" />
                </div>
                <div className="w-6 h-6 rounded-full bg-white/10 text-white/50 text-xs flex items-center justify-center mx-auto mb-3 font-bold">
                  {i + 1}
                </div>
                <h3 className="text-white font-bold text-lg mb-2">{step.title}</h3>
                <p className="text-white/50 text-sm leading-relaxed">{step.desc}</p>
              </motion.div>
            ))}
          </motion.div>
        </section>

        {/* ── ROUTES GRID ── */}
        <section className="py-20 px-4 max-w-6xl mx-auto">
          <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
            className="text-center mb-14">
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-3">SECE Bus Routes</h2>
            <p className="text-white/40 text-sm">Authentic routes from Sri Eshwar College of Engineering transport office</p>
            <div className="w-16 h-1 bg-gradient-to-r from-blue-600 to-teal-500 rounded-full mx-auto mt-4" />
          </motion.div>
          <motion.div variants={container} initial="hidden" whileInView="show" viewport={{ once: true }}
            className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
            {SECE_ROUTES.map(route => (
              <motion.div key={route.id} variants={item}>
                <Link to={`/routes/${route.id}`}
                  className="block bg-white/5 hover:bg-white/10 border border-white/10 hover:border-sky-500/30 rounded-2xl p-5 text-center transition-all group">
                  <span className="inline-block px-2 py-0.5 bg-gradient-to-r from-blue-600 to-teal-500 text-white text-xs font-bold rounded-lg mb-3">
                    {route.num}
                  </span>
                  <p className="text-white text-sm font-semibold leading-snug mb-3">{route.name}</p>
                  <p className="text-sky-400 text-xs font-medium group-hover:text-sky-300 transition-colors flex items-center justify-center gap-1">
                    View Stops <ArrowRight className="w-3 h-3" />
                  </p>
                </Link>
              </motion.div>
            ))}
          </motion.div>
        </section>

        {/* ── DEMO ACCESS ── */}
        <section className="py-20 px-4 max-w-4xl mx-auto">
          <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
            className="text-center mb-14">
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-3">Try Demo Access</h2>
            <p className="text-white/40 text-sm">Pre-seeded accounts — click to log in instantly</p>
            <div className="w-16 h-1 bg-gradient-to-r from-blue-600 to-teal-500 rounded-full mx-auto mt-4" />
          </motion.div>
          <motion.div variants={container} initial="hidden" whileInView="show" viewport={{ once: true }}
            className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {DEMO_ROLES.map(role => {
              const cred = DEMO_CREDENTIALS[role.key];
              return (
                <motion.div key={role.key} variants={item}
                  className={`bg-white/5 backdrop-blur-md border ${role.border} rounded-2xl p-6 text-center`}>
                  <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${role.color} flex items-center justify-center mx-auto mb-4 shadow-lg`}>
                    <role.icon className="w-7 h-7 text-white" />
                  </div>
                  <h3 className="text-white font-bold text-lg mb-1">{role.label}</h3>
                  <p className="text-white/40 text-xs mb-1">{cred.email}</p>
                  <p className="text-white/40 text-xs mb-5">Password: {cred.password}</p>
                  <button
                    onClick={() => handleDemo(role.key, role.dest)}
                    className={`w-full py-2.5 bg-gradient-to-r ${role.color} hover:opacity-90 text-white text-sm font-semibold rounded-xl transition-all shadow-lg`}
                  >
                    Quick Login as {role.label}
                  </button>
                </motion.div>
              );
            })}
          </motion.div>
        </section>

        {/* ── FOOTER ── */}
        <footer className="border-t border-white/5 py-10 px-4 text-center">
          <p className="text-white/30 text-sm mb-2">
            © 2024 BusFlow · Sri Eshwar College of Engineering, Coimbatore, Tamil Nadu, India
          </p>
          <p className="text-white/20 text-xs mb-1">
            Weather:{' '}
            <a href="https://open-meteo.com" className="underline hover:text-white/40" target="_blank" rel="noopener noreferrer">
              Open-Meteo
            </a>{' '}
            (CC BY 4.0) · Maps: OpenStreetMap contributors (ODbL)
          </p>
          <p className="text-white/20 text-xs">
            ML predictions use HistGradientBoosting Regressor trained on synthetic SECE-pattern data · Simulated-Data Performance
          </p>
        </footer>
      </div>
    </div>
  );
}
