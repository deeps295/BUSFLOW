import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Bus, 
  Mail, 
  Lock, 
  Eye, 
  EyeOff, 
  Compass, 
  Gauge, 
  ShieldCheck, 
  ArrowRight, 
  Loader2, 
  AlertCircle,
  Sparkles
} from 'lucide-react';
import BubbleBackground from '../components/layout/BubbleBackground';
import { useAuth, DEMO_CREDENTIALS } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import api from '../services/api';

export const LoginPage = () => {
  const navigate = useNavigate();
  const { login, quickDemoLogin, resetPassword, directTokenLogin } = useAuth();
  const { showToast } = useToast();

  const [activeTab, setActiveTab] = useState('STUDENT'); // STUDENT | DRIVER | ADMIN
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  // Password reset inline state
  const [showResetBox, setShowResetBox] = useState(false);
  const [resetUsernameOrEmail, setResetUsernameOrEmail] = useState('');
  const [newPasswordVal, setNewPasswordVal] = useState('');
  const [resetLoading, setResetLoading] = useState(false);

  const navigateByRole = (role) => {
    if (role === 'ADMIN') navigate('/admin');
    else if (role === 'DRIVER') navigate('/driver');
    else navigate('/student');
  };

  const handleTabChange = (role) => {
    setActiveTab(role);
    setErrorMsg('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    if (!email.trim() || !password) {
      setErrorMsg('Please enter both email/username and password');
      return;
    }

    setLoading(true);
    try {
      const user = await login(email.trim(), password);
      if (showToast) {
        showToast(`Welcome back, ${user?.full_name || user?.username || 'User'}!`, 'success');
      }
      navigateByRole(user?.role);
    } catch (err) {
      let detail =
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        null;

      if (!detail) {
        if (typeof err?.response?.data === 'string' && (err.response.data.includes('ECONNREFUSED') || err.response.data.includes('Proxy error'))) {
          detail = 'Cannot connect to backend server on port 8001. Please start backend with: python run_backend.py';
        } else if (err?.message && (err.message.includes('Network') || err.message.includes('code 500') || err.message.includes('ECONNREFUSED'))) {
          detail = 'Backend server on port 8001 is unreachable. Please verify "python run_backend.py" is running in Terminal 1.';
        } else {
          detail = err?.message || 'Invalid email or password. Please try again.';
        }
      }

      setErrorMsg(detail);
      if (showToast) {
        showToast(detail, 'error');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDemoQuickLogin = async (roleKey) => {
    setErrorMsg('');
    setLoading(true);
    try {
      const user = await quickDemoLogin(roleKey);
      if (showToast) {
        showToast(`Signed in with ${DEMO_CREDENTIALS[roleKey]?.name || roleKey} demo access!`, 'success');
      }
      navigateByRole(user?.role || DEMO_CREDENTIALS[roleKey]?.role || 'STUDENT');
    } catch (err) {
      const detail = err?.response?.data?.detail || err?.response?.data?.message || `Failed to sign in as ${roleKey} demo user.`;
      setErrorMsg(detail);
      if (showToast) {
        showToast(detail, 'error');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleInlineResetPassword = async (e) => {
    e.preventDefault();
    const targetId = resetUsernameOrEmail.trim() || email.trim();
    if (!targetId) {
      setErrorMsg('Please enter your email or username to reset password.');
      return;
    }
    if (!newPasswordVal || newPasswordVal.length < 6) {
      setErrorMsg('New password must be at least 6 characters.');
      return;
    }

    setResetLoading(true);
    setErrorMsg('');
    try {
      await resetPassword(targetId, newPasswordVal);
      if (showToast) {
        showToast('Password reset successfully! Logging you in...', 'success');
      }
      // Automatically login with the newly set password
      const user = await login(targetId, newPasswordVal);
      setShowResetBox(false);
      navigateByRole(user?.role);
    } catch (err) {
      const detail = err?.response?.data?.detail || err?.response?.data?.message || 'Failed to reset password.';
      setErrorMsg(detail);
    } finally {
      setResetLoading(false);
    }
  };

  return (
    <div 
      className="min-h-screen relative flex items-center justify-center p-4 sm:p-6 overflow-hidden text-white font-sans selection:bg-cyan-500/30"
      style={{ background: 'linear-gradient(135deg, #071B3A 0%, #0F2D5E 50%, #071B3A 100%)' }}
    >
      <BubbleBackground />

      <motion.div 
        initial={{ opacity: 0, y: 25, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        className="relative z-10 w-full max-w-md bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 sm:p-8 shadow-2xl shadow-black/40"
      >
        {/* Logo & Heading */}
        <div className="text-center mb-6">
          <Link to="/" className="inline-flex items-center gap-2 mb-3 group">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-blue-600 via-cyan-500 to-teal-400 p-0.5 shadow-lg shadow-cyan-500/20 group-hover:scale-105 transition-transform">
              <div className="w-full h-full bg-[#071B3A]/90 rounded-[14px] flex items-center justify-center">
                <Bus className="w-6 h-6 text-cyan-300" />
              </div>
            </div>
          </Link>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight bg-gradient-to-r from-sky-300 via-cyan-400 to-teal-300 bg-clip-text text-transparent">
            Welcome Back
          </h1>
          <p className="text-xs text-white/60 mt-1">
            Sign in to access your SECE BusFlow dashboard
          </p>
        </div>

        {/* Role Selector Tabs */}
        <div className="grid grid-cols-3 gap-1 bg-slate-900/60 p-1 rounded-xl border border-white/5 mb-6">
          <button
            type="button"
            onClick={() => handleTabChange('STUDENT')}
            className={`flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'STUDENT'
                ? 'bg-gradient-to-r from-blue-600 to-cyan-500 text-white shadow-md'
                : 'text-white/60 hover:text-white hover:bg-white/5'
            }`}
          >
            <Compass className="w-3.5 h-3.5" />
            <span>Student</span>
          </button>

          <button
            type="button"
            onClick={() => handleTabChange('DRIVER')}
            className={`flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'DRIVER'
                ? 'bg-gradient-to-r from-cyan-600 to-teal-500 text-white shadow-md'
                : 'text-white/60 hover:text-white hover:bg-white/5'
            }`}
          >
            <Gauge className="w-3.5 h-3.5" />
            <span>Driver</span>
          </button>

          <button
            type="button"
            onClick={() => handleTabChange('ADMIN')}
            className={`flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'ADMIN'
                ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-md'
                : 'text-white/60 hover:text-white hover:bg-white/5'
            }`}
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Admin</span>
          </button>
        </div>

        {/* Error Box */}
        <AnimatePresence>
          {errorMsg && (
            <motion.div
              initial={{ opacity: 0, height: 0, marginBottom: 0 }}
              animate={{ opacity: 1, height: 'auto', marginBottom: 16 }}
              exit={{ opacity: 0, height: 0, marginBottom: 0 }}
              className="flex items-center gap-2 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs font-medium"
            >
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
              <span>{errorMsg}</span>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-sky-300 mb-1.5">
              Email or Username
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-white/40 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder={DEMO_CREDENTIALS[activeTab]?.email || 'user@sece.ac.in'}
                className="w-full bg-white/10 border border-white/20 rounded-xl pl-10 pr-4 py-3 text-white placeholder-white/30 text-sm focus:outline-none focus:border-sky-400 focus:ring-1 focus:ring-sky-400 transition-all"
                disabled={loading}
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-sky-300 mb-1.5">
              Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-white/40 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-white/10 border border-white/20 rounded-xl pl-10 pr-10 py-3 text-white placeholder-white/30 text-sm focus:outline-none focus:border-sky-400 focus:ring-1 focus:ring-sky-400 transition-all"
                disabled={loading}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3.5 top-1/2 -translate-y-1/2 text-white/40 hover:text-white transition-colors"
                tabIndex={-1}
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            {/* Forgot / Reset Password Toggle */}
            <div className="flex justify-end items-center mt-1.5">
              <button
                type="button"
                onClick={() => {
                  setResetUsernameOrEmail(email);
                  setShowResetBox(!showResetBox);
                }}
                className="text-[11px] text-sky-400 hover:text-sky-300 hover:underline"
              >
                {showResetBox ? 'Hide Reset' : 'Forgot / Reset Password?'}
              </button>
            </div>
          </div>

          {/* Inline Password Reset Box */}
          <AnimatePresence>
            {showResetBox && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="p-3.5 rounded-xl bg-cyan-950/70 border border-cyan-500/40 text-xs space-y-2.5"
              >
                <div className="flex items-center gap-2 text-cyan-300 font-semibold">
                  <Sparkles className="w-4 h-4 text-cyan-400" />
                  <span>Instant Password Reset (External Review Safe)</span>
                </div>
                <p className="text-[11px] text-white/70">
                  Enter your email/username and new password to reset it immediately:
                </p>
                <div className="space-y-2">
                  <input
                    type="text"
                    value={resetUsernameOrEmail}
                    onChange={(e) => setResetUsernameOrEmail(e.target.value)}
                    placeholder="Username or email (e.g. deepika)"
                    className="w-full bg-black/40 border border-cyan-500/30 rounded-lg px-3 py-1.5 text-xs text-white placeholder-white/40 focus:outline-none focus:border-cyan-400"
                  />
                  <input
                    type="password"
                    value={newPasswordVal}
                    onChange={(e) => setNewPasswordVal(e.target.value)}
                    placeholder="New password (min 6 chars, e.g. deepika123)"
                    className="w-full bg-black/40 border border-cyan-500/30 rounded-lg px-3 py-1.5 text-xs text-white placeholder-white/40 focus:outline-none focus:border-cyan-400"
                  />
                  <button
                    type="button"
                    onClick={handleInlineResetPassword}
                    disabled={resetLoading}
                    className="w-full py-2 bg-gradient-to-r from-cyan-600 to-teal-500 hover:from-cyan-500 hover:to-teal-400 text-white font-bold rounded-lg text-xs transition-all shadow flex items-center justify-center gap-1.5 disabled:opacity-50"
                  >
                    {resetLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : null}
                    <span>Reset Password & Sign In</span>
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-blue-600 via-cyan-600 to-teal-500 hover:from-blue-500 hover:via-cyan-500 hover:to-teal-400 text-white font-semibold py-3 px-6 rounded-xl transition-all shadow-lg shadow-cyan-500/20 flex items-center justify-center gap-2 text-sm disabled:opacity-50 disabled:cursor-not-allowed group mt-2"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Signing in...</span>
              </>
            ) : (
              <>
                <span>Sign In as {activeTab}</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </>
            )}
          </button>
        </form>

        {/* Divider */}
        <div className="relative my-6 text-center">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-white/10" />
          </div>
          <span className="relative px-3 bg-[#0c244c] text-[11px] uppercase tracking-wider text-white/40 font-semibold rounded-full">
            or 1-click external review demo access
          </span>
        </div>

        {/* 1-Click Review Access Buttons */}
        <div className="space-y-2">
          {/* Deepika T. Spotlight Card */}
          <button
            type="button"
            onClick={() => handleDemoQuickLogin('DEEPIKA')}
            disabled={loading}
            className="w-full p-2.5 rounded-xl bg-gradient-to-r from-sky-600/20 to-cyan-600/20 hover:from-sky-600/30 hover:to-cyan-600/30 border border-sky-400/40 text-left flex items-center justify-between transition-all hover:scale-[1.01] group disabled:opacity-40"
          >
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-sky-500/30 flex items-center justify-center text-sky-300 font-bold text-xs">
                🎓
              </div>
              <div>
                <div className="flex items-center gap-1.5">
                  <span className="text-xs font-bold text-sky-200">Deepika T.</span>
                  <span className="text-[10px] px-1.5 py-0.2 rounded bg-sky-500/20 text-sky-300 border border-sky-400/30">AI&DS (24AD038)</span>
                </div>
                <p className="text-[10px] text-white/50">deepika@sece.ac.in · Single-click Student Portal</p>
              </div>
            </div>
            <ArrowRight className="w-4 h-4 text-sky-300 group-hover:translate-x-1 transition-transform" />
          </button>

          {/* Grid of Other Roles */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1">
            <button
              type="button"
              onClick={() => handleDemoQuickLogin('STUDENT')}
              disabled={loading}
              className="p-2 rounded-xl bg-white/5 hover:bg-white/10 border border-cyan-500/30 text-cyan-300 text-xs font-semibold flex flex-col items-center gap-1 transition-all hover:scale-[1.02] disabled:opacity-40"
            >
              <Compass className="w-3.5 h-3.5 text-cyan-400" />
              <span className="text-[11px]">Karthik (CSE)</span>
            </button>

            <button
              type="button"
              onClick={() => handleDemoQuickLogin('DRIVER')}
              disabled={loading}
              className="p-2 rounded-xl bg-white/5 hover:bg-white/10 border border-teal-500/30 text-teal-300 text-xs font-semibold flex flex-col items-center gap-1 transition-all hover:scale-[1.02] disabled:opacity-40"
            >
              <Gauge className="w-3.5 h-3.5 text-teal-400" />
              <span className="text-[11px]">Driver Selvam</span>
            </button>

            <button
              type="button"
              onClick={() => handleDemoQuickLogin('ADMIN')}
              disabled={loading}
              className="p-2 rounded-xl bg-white/5 hover:bg-white/10 border border-purple-500/30 text-purple-300 text-xs font-semibold flex flex-col items-center gap-1 transition-all hover:scale-[1.02] disabled:opacity-40"
            >
              <ShieldCheck className="w-3.5 h-3.5 text-purple-400" />
              <span className="text-[11px]">SECE Admin</span>
            </button>

            <button
              type="button"
              onClick={() => handleDemoQuickLogin('REVIEWER')}
              disabled={loading}
              className="p-2 rounded-xl bg-gradient-to-tr from-amber-600/30 to-rose-600/30 hover:from-amber-600/40 hover:to-rose-600/40 border border-amber-500/40 text-amber-200 text-xs font-semibold flex flex-col items-center gap-1 transition-all hover:scale-[1.02] disabled:opacity-40"
            >
              <Sparkles className="w-3.5 h-3.5 text-amber-300" />
              <span className="text-[11px]">Reviewer Pass</span>
            </button>
          </div>
        </div>

        {/* Register link */}
        <div className="text-center mt-6 pt-4 border-t border-white/5">
          <p className="text-xs text-white/60">
            Don't have an account?{' '}
            <Link to="/register" className="text-sky-300 hover:text-sky-200 font-semibold underline underline-offset-4">
              Register here
            </Link>
          </p>
          <div className="mt-3">
            <Link to="/" className="text-[11px] text-white/40 hover:text-white/70 transition-colors">
              ← Return to BusFlow Home
            </Link>
          </div>
        </div>

      </motion.div>
    </div>
  );
};

export default LoginPage;
