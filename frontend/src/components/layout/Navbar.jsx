import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Bus, Menu, X, LogOut, User, Shield, Car, GraduationCap, BarChart2, Map } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import useBackendStatus from '../../hooks/useBackendStatus';

const NAV_LINKS = {
  STUDENT: [
    { label: 'My Bus', to: '/student', icon: Bus },
  ],
  DRIVER: [
    { label: 'My Route', to: '/driver', icon: Map },
  ],
  ADMIN: [
    { label: 'Dashboard', to: '/admin', icon: BarChart2 },
    { label: 'ML Analytics', to: '/admin/ml', icon: BarChart2 },
  ],
  GUEST: [],
};

const ROLE_ICON = { ADMIN: Shield, DRIVER: Car, STUDENT: GraduationCap };
const ROLE_COLOR = { ADMIN: 'text-purple-400', DRIVER: 'text-orange-400', STUDENT: 'text-sky-400' };

const Navbar = () => {
  const { currentUser, isAuthenticated, userRole, logout } = useAuth();
  const { isConnected } = useBackendStatus(15000);
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  const links = NAV_LINKS[userRole] || [];
  const RoleIcon = ROLE_ICON[userRole] || User;

  const handleLogout = () => {
    logout();
    navigate('/');
    setMobileOpen(false);
  };

  return (
    <nav className="relative z-50 sticky top-0 bg-white/5 backdrop-blur-xl border-b border-white/10">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between gap-4">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2.5 flex-shrink-0 group">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-600 to-teal-500 flex items-center justify-center shadow-lg shadow-blue-900/40">
            <Bus className="w-5 h-5 text-white" />
          </div>
          <div>
            <span className="text-white font-bold text-lg leading-none">BusFlow</span>
            <p className="text-white/40 text-[10px] leading-none mt-0.5 hidden sm:block">Smart Arrival. Less Waiting.</p>
          </div>
        </Link>

        {/* Desktop nav links */}
        <div className="hidden md:flex items-center gap-1">
          {links.map(link => (
            <Link
              key={link.to}
              to={link.to}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                location.pathname === link.to
                  ? 'bg-white/10 text-white'
                  : 'text-white/60 hover:text-white hover:bg-white/5'
              }`}
            >
              <link.icon className="w-4 h-4" />
              {link.label}
            </Link>
          ))}
        </div>

        {/* Right section */}
        <div className="flex items-center gap-3">
          {/* Backend status */}
          <div className={`hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${
            isConnected
              ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
              : 'bg-red-500/10 border-red-500/20 text-red-400'
          }`}>
            <span className={`w-1.5 h-1.5 rounded-full ${isConnected ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'}`} />
            {isConnected ? 'Live' : 'Offline'}
          </div>

          {isAuthenticated ? (
            <div className="hidden md:flex items-center gap-2">
              <div className="flex items-center gap-2 px-3 py-1.5 bg-white/5 rounded-xl border border-white/10">
                <RoleIcon className={`w-4 h-4 ${ROLE_COLOR[userRole] || 'text-white'}`} />
                <span className="text-white text-sm font-medium max-w-[120px] truncate">
                  {currentUser?.full_name || currentUser?.username || 'User'}
                </span>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center gap-1.5 px-3 py-1.5 text-white/50 hover:text-white hover:bg-white/10 rounded-xl text-sm transition-all"
              >
                <LogOut className="w-4 h-4" />
                <span className="hidden lg:inline">Logout</span>
              </button>
            </div>
          ) : (
            <div className="hidden md:flex items-center gap-2">
              <Link to="/login" className="px-4 py-2 text-white/70 hover:text-white text-sm font-medium transition-colors">
                Sign In
              </Link>
              <Link to="/register" className="px-4 py-2 bg-gradient-to-r from-blue-600 to-teal-500 text-white text-sm font-semibold rounded-xl hover:opacity-90 transition-opacity">
                Register
              </Link>
            </div>
          )}

          {/* Mobile hamburger */}
          <button
            onClick={() => setMobileOpen(v => !v)}
            className="md:hidden p-2 text-white/60 hover:text-white hover:bg-white/10 rounded-xl transition-all"
          >
            {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden border-t border-white/10 bg-white/5 backdrop-blur-xl px-4 py-3 space-y-1"
          >
            {links.map(link => (
              <Link
                key={link.to}
                to={link.to}
                onClick={() => setMobileOpen(false)}
                className="flex items-center gap-2 px-4 py-3 rounded-xl text-white/70 hover:text-white hover:bg-white/10 text-sm font-medium transition-all"
              >
                <link.icon className="w-4 h-4" />
                {link.label}
              </Link>
            ))}
            {isAuthenticated ? (
              <>
                <div className="flex items-center gap-2 px-4 py-3 text-white/60 text-sm">
                  <RoleIcon className={`w-4 h-4 ${ROLE_COLOR[userRole] || 'text-white'}`} />
                  {currentUser?.full_name || 'User'} · {userRole}
                </div>
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-2 px-4 py-3 rounded-xl text-red-400 hover:bg-red-500/10 text-sm font-medium transition-all"
                >
                  <LogOut className="w-4 h-4" />
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/login" onClick={() => setMobileOpen(false)} className="flex px-4 py-3 rounded-xl text-white/70 hover:text-white hover:bg-white/10 text-sm font-medium transition-all">
                  Sign In
                </Link>
                <Link to="/register" onClick={() => setMobileOpen(false)} className="flex px-4 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-teal-500 text-white text-sm font-semibold transition-all">
                  Register
                </Link>
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
};

export default Navbar;
