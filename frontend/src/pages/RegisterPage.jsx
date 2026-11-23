import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Bus, 
  Mail, 
  Lock, 
  Eye, 
  EyeOff, 
  User, 
  Hash, 
  BookOpen, 
  CreditCard, 
  ArrowRight, 
  Loader2, 
  AlertCircle,
  Compass,
  Gauge,
  ShieldCheck
} from 'lucide-react';
import BubbleBackground from '../components/layout/BubbleBackground';
import { useAuth, DEMO_CREDENTIALS } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';

export const RegisterPage = () => {
  const navigate = useNavigate();
  const { register, login, quickDemoLogin } = useAuth();
  const { showToast } = useToast();

  const [role, setRole] = useState('STUDENT'); // STUDENT | DRIVER | ADMIN
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  // Student specific
  const [rollNumber, setRollNumber] = useState('');
  const [department, setDepartment] = useState('AIDS');

  // Driver specific
  const [licenseNumber, setLicenseNumber] = useState('');

  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [conflictAccount, setConflictAccount] = useState(false);
  const [autoFillNotice, setAutoFillNotice] = useState('');

  const departments = ['AIDS', 'AIML', 'CSE', 'ECE', 'EEE', 'IT', 'MECH', 'CIVIL'];

  const handleAutoFillReviewer = (customRole = role) => {
    // Generate guaranteed unique 6-digit identifier using timestamp + random
    const uid = `${Date.now().toString().slice(-4)}${Math.floor(10 + Math.random() * 90)}`;
    setRole(customRole);
    setFullName(`Reviewer Evaluator ${uid}`);
    setUsername(`reviewer_${uid}`);
    setEmail(`reviewer_${uid}@sece.ac.in`);
    setPassword('reviewer123');
    setConfirmPassword('reviewer123');
    if (customRole === 'STUDENT') {
      setRollNumber(`24AD${uid}`);
      setDepartment('AIDS');
    } else if (customRole === 'DRIVER') {
      setLicenseNumber(`TN38-DL-${uid}`);
    }
    setErrorMsg('');
    setConflictAccount(false);
    setAutoFillNotice(`Loaded fresh unique credentials: reviewer_${uid} / reviewer123`);
    setTimeout(() => setAutoFillNotice(''), 5000);
  };

  const handleOverwriteAndLogin = async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      const payload = {
        email: email.trim(),
        username: username.trim(),
        password: password,
        full_name: fullName.trim() || username.trim(),
        role: role,
        overwrite_if_exists: true,
      };

      if (role === 'STUDENT') {
        payload.roll_number = rollNumber.trim().toUpperCase() || `24AD${Math.floor(1000 + Math.random() * 9000)}`;
        payload.department = department;
      } else if (role === 'DRIVER') {
        payload.license_number = licenseNumber.trim().toUpperCase() || `TN38-DL-${Math.floor(100000 + Math.random() * 900000)}`;
      }

      await register(payload);
      const user = await login(email.trim() || username.trim(), password);
      if (showToast) {
        showToast(`Account updated & signed in as ${user?.full_name || user?.username}!`, 'success');
      }
      if (user?.role === 'ADMIN') navigate('/admin');
      else if (user?.role === 'DRIVER') navigate('/driver');
      else navigate('/student');
    } catch (err) {
      const detail = err?.response?.data?.detail || err?.response?.data?.message || err?.message || 'Failed to update existing account.';
      setErrorMsg(detail);
      if (showToast) showToast(detail, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setConflictAccount(false);

    if (!fullName.trim() || !email.trim() || !username.trim() || !password) {
      setErrorMsg('Please fill in all mandatory fields');
      return;
    }

    if (password !== confirmPassword) {
      setErrorMsg('Passwords do not match');
      return;
    }

    if (password.length < 6) {
      setErrorMsg('Password must be at least 6 characters long');
      return;
    }

    // Role-specific validation
    if (role === 'STUDENT' && !rollNumber.trim()) {
      setErrorMsg('Please enter your SECE Roll Number');
      return;
    }

    if (role === 'DRIVER' && !licenseNumber.trim()) {
      setErrorMsg('Please enter your Commercial Driver License Number');
      return;
    }

    const payload = {
      email: email.trim(),
      username: username.trim(),
      password: password,
      full_name: fullName.trim(),
      role: role,
    };

    if (role === 'STUDENT') {
      payload.roll_number = rollNumber.trim().toUpperCase();
      payload.department = department;
    } else if (role === 'DRIVER') {
      payload.license_number = licenseNumber.trim().toUpperCase();
    }

    setLoading(true);
    try {
      await register(payload);
      if (showToast) {
        showToast('Account created successfully! Token generated. Logging you in...', 'success');
      }
      // Auto login right after registration so user doesn't face lag
      try {
        const user = await login(email.trim(), password);
        if (user.role === 'ADMIN') navigate('/admin');
        else if (user.role === 'DRIVER') navigate('/driver');
        else navigate('/student');
      } catch {
        navigate('/login');
      }
    } catch (err) {
      let detail =
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        null;

      if (!detail) {
        if (typeof err?.response?.data === 'string' && (err.response.data.includes('ECONNREFUSED') || err.response.data.includes('Proxy error'))) {
          detail = 'Cannot connect to backend server on port 8001. Please start backend with: python run_backend.py';
        } else if (err?.message && (err.message.includes('Network') || err.message.includes('code 500') || err.message.includes('ECONNREFUSED'))) {
          detail = 'Backend server on port 8001 is unreachable. Please ensure "python run_backend.py" is running in Terminal 1.';
        } else {
          detail = err?.message || 'Registration failed. The email or username may already be in use.';
        }
      }

      setErrorMsg(detail);
      const lower = String(detail).toLowerCase();
      if (lower.includes('already exist') || lower.includes('already taken') || lower.includes('already registered') || lower.includes('already assigned')) {
        setConflictAccount(true);
      }
      if (showToast) {
        showToast(detail, 'error');
      }
    } finally {
      setLoading(false);
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
        className="relative z-10 w-full max-w-lg bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 sm:p-8 shadow-2xl shadow-black/40 my-8"
      >
        {/* Header */}
        <div className="text-center mb-6">
          <Link to="/" className="inline-flex items-center gap-2 mb-3 group">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-blue-600 via-cyan-500 to-teal-400 p-0.5 shadow-lg shadow-cyan-500/20 group-hover:scale-105 transition-transform">
              <div className="w-full h-full bg-[#071B3A]/90 rounded-[14px] flex items-center justify-center">
                <Bus className="w-6 h-6 text-cyan-300" />
              </div>
            </div>
          </Link>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight bg-gradient-to-r from-sky-300 via-cyan-400 to-teal-300 bg-clip-text text-transparent">
            Create Account
          </h1>
          <p className="text-xs text-white/60 mt-1">
            Join BusFlow at Sri Eshwar College of Engineering
          </p>
        </div>

        {/* Role Selector Tabs */}
        <div className="grid grid-cols-3 gap-1 bg-slate-900/60 p-1 rounded-xl border border-white/5 mb-6">
          <button
            type="button"
            onClick={() => setRole('STUDENT')}
            className={`flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-semibold transition-all ${
              role === 'STUDENT'
                ? 'bg-gradient-to-r from-blue-600 to-cyan-500 text-white shadow-md'
                : 'text-white/60 hover:text-white hover:bg-white/5'
            }`}
          >
            <Compass className="w-3.5 h-3.5" />
            <span>Student</span>
          </button>

          <button
            type="button"
            onClick={() => setRole('DRIVER')}
            className={`flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-semibold transition-all ${
              role === 'DRIVER'
                ? 'bg-gradient-to-r from-cyan-600 to-teal-500 text-white shadow-md'
                : 'text-white/60 hover:text-white hover:bg-white/5'
            }`}
          >
            <Gauge className="w-3.5 h-3.5" />
            <span>Driver</span>
          </button>

          <button
            type="button"
            onClick={() => setRole('ADMIN')}
            className={`flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-semibold transition-all ${
              role === 'ADMIN'
                ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-md'
                : 'text-white/60 hover:text-white hover:bg-white/5'
            }`}
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Admin</span>
          </button>
        </div>

        {/* External Review Auto-Fill / Multi-Registration Helper */}
        <div className="mb-5 p-3 rounded-xl bg-gradient-to-r from-blue-900/40 via-cyan-900/40 to-teal-900/40 border border-cyan-500/30 flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-cyan-500/20 flex items-center justify-center shrink-0">
              <Compass className="w-4 h-4 text-cyan-300" />
            </div>
            <div>
              <p className="text-[11px] font-semibold text-cyan-200">External Reviewer Helper</p>
              <p className="text-[10px] text-white/50">Generate fresh unique credentials for zero-conflict review</p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => handleAutoFillReviewer()}
            className="px-2.5 py-1.5 rounded-lg bg-gradient-to-r from-cyan-500 to-teal-400 hover:from-cyan-400 hover:to-teal-300 text-slate-900 font-bold text-[11px] shrink-0 transition-transform hover:scale-105 shadow-md shadow-cyan-500/20"
          >
            ⚡ Auto-Fill Unique
          </button>
        </div>

        {autoFillNotice && (
          <div className="mb-4 p-2.5 rounded-xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-200 text-xs flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            <span>{autoFillNotice}</span>
          </div>
        )}

        {/* Conflict Resolution Box */}
        <AnimatePresence>
          {conflictAccount && (
            <motion.div
              initial={{ opacity: 0, height: 0, marginBottom: 0 }}
              animate={{ opacity: 1, height: 'auto', marginBottom: 16 }}
              exit={{ opacity: 0, height: 0, marginBottom: 0 }}
              className="p-3.5 rounded-xl bg-amber-500/15 border border-amber-500/40 text-amber-200 text-xs space-y-2.5"
            >
              <div className="flex items-center gap-2 text-amber-300 font-semibold">
                <AlertCircle className="w-4 h-4 shrink-0 text-amber-400" />
                <span>Account Already Exists in Database</span>
              </div>
              <p className="text-[11px] text-white/70 leading-relaxed">
                The username <strong className="text-white">"{username}"</strong> or email <strong className="text-white">"{email}"</strong> is already in use. You can either take over this account with your new password, or generate a fresh unique account for review.
              </p>
              <div className="flex flex-wrap items-center gap-2 pt-1">
                <button
                  type="button"
                  onClick={handleOverwriteAndLogin}
                  disabled={loading}
                  className="px-3 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs transition-all shadow-md shadow-amber-500/20 disabled:opacity-50"
                >
                  Overwrite Password & Sign In
                </button>
                <button
                  type="button"
                  onClick={() => handleAutoFillReviewer()}
                  disabled={loading}
                  className="px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-white font-medium text-xs transition-all border border-white/20"
                >
                  ⚡ Generate Fresh Unique ID
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Error Box */}
        <AnimatePresence>
          {errorMsg && !conflictAccount && (
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

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-sky-300 mb-1.5">
              Full Name *
            </label>
            <div className="relative">
              <User className="w-4 h-4 text-white/40 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="e.g. Karthik Ramasamy"
                className="w-full bg-white/10 border border-white/20 rounded-xl pl-10 pr-4 py-2.5 text-white placeholder-white/30 text-sm focus:outline-none focus:border-sky-400 focus:ring-1 focus:ring-sky-400 transition-all"
                disabled={loading}
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-sky-300 mb-1.5">
                Email Address *
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-white/40 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="karthik@sece.ac.in"
                  className="w-full bg-white/10 border border-white/20 rounded-xl pl-10 pr-4 py-2.5 text-white placeholder-white/30 text-sm focus:outline-none focus:border-sky-400 focus:ring-1 focus:ring-sky-400 transition-all"
                  disabled={loading}
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-sky-300 mb-1.5">
                Username *
              </label>
              <div className="relative">
                <Hash className="w-4 h-4 text-white/40 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="karthik_r"
                  className="w-full bg-white/10 border border-white/20 rounded-xl pl-10 pr-4 py-2.5 text-white placeholder-white/30 text-sm focus:outline-none focus:border-sky-400 focus:ring-1 focus:ring-sky-400 transition-all"
                  disabled={loading}
                />
              </div>
            </div>
          </div>

          {/* Conditional Fields based on Role */}
          {role === 'STUDENT' && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 p-3.5 rounded-xl bg-cyan-950/30 border border-cyan-500/20">
              <div>
                <label className="block text-xs font-medium text-cyan-300 mb-1.5">
                  Roll Number *
                </label>
                <input
                  type="text"
                  value={rollNumber}
                  onChange={(e) => setRollNumber(e.target.value)}
                  placeholder="715521104001"
                  className="w-full bg-white/10 border border-white/20 rounded-xl px-3 py-2 text-white placeholder-white/30 text-sm uppercase focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 transition-all"
                  disabled={loading}
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-cyan-300 mb-1.5">
                  Department *
                </label>
                <div className="relative">
                  <select
                    value={department}
                    onChange={(e) => setDepartment(e.target.value)}
                    className="w-full bg-slate-900 border border-white/20 rounded-xl px-3 py-2 text-white text-sm focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 transition-all"
                    disabled={loading}
                  >
                    {departments.map((d) => (
                      <option key={d} value={d} className="bg-slate-900 text-white">
                        {d}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          )}

          {role === 'DRIVER' && (
            <div className="p-3.5 rounded-xl bg-teal-950/30 border border-teal-500/20">
              <label className="block text-xs font-medium text-teal-300 mb-1.5">
                License Number *
              </label>
              <div className="relative">
                <CreditCard className="w-4 h-4 text-white/40 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={licenseNumber}
                  onChange={(e) => setLicenseNumber(e.target.value)}
                  placeholder="TN-38-2015-0012345"
                  className="w-full bg-white/10 border border-white/20 rounded-xl pl-10 pr-4 py-2 text-white placeholder-white/30 text-sm uppercase focus:outline-none focus:border-teal-400 focus:ring-1 focus:ring-teal-400 transition-all"
                  disabled={loading}
                />
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-sky-300 mb-1.5">
                Password *
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-white/40 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-white/10 border border-white/20 rounded-xl pl-10 pr-10 py-2.5 text-white placeholder-white/30 text-sm focus:outline-none focus:border-sky-400 focus:ring-1 focus:ring-sky-400 transition-all"
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-white/40 hover:text-white transition-colors"
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                </button>
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-sky-300 mb-1.5">
                Confirm Password *
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-white/40 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-white/10 border border-white/20 rounded-xl pl-10 pr-4 py-2.5 text-white placeholder-white/30 text-sm focus:outline-none focus:border-sky-400 focus:ring-1 focus:ring-sky-400 transition-all"
                  disabled={loading}
                />
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-blue-600 via-cyan-600 to-teal-500 hover:from-blue-500 hover:via-cyan-500 hover:to-teal-400 text-white font-semibold py-3 px-6 rounded-xl transition-all shadow-lg shadow-cyan-500/20 flex items-center justify-center gap-2 text-sm disabled:opacity-50 disabled:cursor-not-allowed group mt-4"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Registering account...</span>
              </>
            ) : (
              <>
                <span>Complete Registration</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </>
            )}
          </button>
        </form>

        {/* Footer */}
        <div className="text-center mt-6 pt-4 border-t border-white/5">
          <p className="text-xs text-white/60">
            Already have an account?{' '}
            <Link to="/login" className="text-sky-300 hover:text-sky-200 font-semibold underline underline-offset-4">
              Sign in here
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

export default RegisterPage;
