import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const DEMO_CREDENTIALS = {
  DEEPIKA: {
    email: 'deepika@sece.ac.in',
    username: 'deepika',
    password: 'deepika123',
    role: 'STUDENT',
    name: 'Deepika T. (AI&DS Dept)',
    roll: '24AD038'
  },
  STUDENT: {
    email: 'student@sece.ac.in',
    username: 'student_karthik',
    password: 'student123',
    role: 'STUDENT',
    name: 'Karthik R. (CSE Dept)',
    roll: '718121104042'
  },
  DRIVER: {
    email: 'driver@sece.ac.in',
    username: 'driver_selvam',
    password: 'driver123',
    role: 'DRIVER',
    name: 'Selvam K. (Senior Driver)',
    license: 'TN38-DL-000002'
  },
  ADMIN: {
    email: 'admin@sece.ac.in',
    username: 'admin',
    password: 'admin123',
    role: 'ADMIN',
    name: 'SECE Transport Admin'
  },
  REVIEWER: {
    email: 'reviewer@sece.ac.in',
    username: 'reviewer_external',
    password: 'reviewer123',
    role: 'ADMIN',
    name: 'External Reviewer / Examiner'
  }
};

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('busflow_token') || null);
  const [isLoading, setIsLoading] = useState(true);

  // Load session from token on mount
  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('busflow_token');
      if (storedToken) {
        try {
          const res = await api.get('/auth/me');
          setCurrentUser(res.data);
        } catch (err) {
          console.warn('[Auth] Stored session expired or invalid:', err.message);
          localStorage.removeItem('busflow_token');
          setToken(null);
          setCurrentUser(null);
        }
      }
      setIsLoading(false);
    };
    initAuth();
  }, []);

  const login = async (usernameOrEmail, password) => {
    const res = await api.post('/auth/login', {
      username_or_email: usernameOrEmail.trim(),
      password: password,
    });
    const { access_token, user } = res.data;
    localStorage.setItem('busflow_token', access_token);
    setToken(access_token);
    setCurrentUser(user);
    return user;
  };

  const register = async (userData) => {
    const res = await api.post('/auth/register', userData);
    return res.data;
  };

  const resetPassword = async (usernameOrEmail, newPassword) => {
    const res = await api.post('/auth/reset-password', {
      username_or_email: usernameOrEmail.trim(),
      new_password: newPassword,
    });
    return res.data;
  };

  const directTokenLogin = (accessToken, user) => {
    localStorage.setItem('busflow_token', accessToken);
    setToken(accessToken);
    setCurrentUser(user);
    return user;
  };

  const quickDemoLogin = async (roleKey) => {
    const cred = DEMO_CREDENTIALS[roleKey];
    if (!cred) return null;
    return await login(cred.email, cred.password);
  };

  const logout = () => {
    localStorage.removeItem('busflow_token');
    setToken(null);
    setCurrentUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        currentUser,
        token,
        isLoading,
        isAuthenticated: !!currentUser,
        userRole: currentUser?.role || 'GUEST',
        login,
        register,
        resetPassword,
        directTokenLogin,
        quickDemoLogin,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
export default AuthContext;
