import axios from 'axios';

// Create central Axios client
export const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to attach JWT auth token if stored
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('busflow_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for consistent error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.response?.data?.message || error.message || 'Network communication error';
    console.error('[API Error]:', message);
    return Promise.reject(error);
  }
);

// Health check service
export const checkBackendHealth = async () => {
  try {
    const response = await api.get('/health');
    return { ok: true, data: response.data };
  } catch (error) {
    return { ok: false, error: error.message };
  }
};

export default api;
