import api from './api';

export const adminService = {
  getDashboard: () => api.get('/admin/dashboard').then(r => r.data),
  getModelMetrics: () => api.get('/admin/model/metrics').then(r => r.data),
  getModelHistory: () => api.get('/admin/model/history').then(r => r.data),
  triggerTraining: () => api.post('/admin/model/train').then(r => r.data),
  getRoutes: () => api.get('/admin/routes').then(r => r.data),

  // Drivers Management
  getDrivers: () => api.get('/admin/drivers').then(r => r.data),
  createDriver: (data) => api.post('/admin/drivers', data).then(r => r.data),
  updateDriver: (id, data) => api.put(`/admin/drivers/${id}`, data).then(r => r.data),
  deleteDriver: (id) => api.delete(`/admin/drivers/${id}`).then(r => r.data),

  // Students Management
  getStudents: () => api.get('/admin/students').then(r => r.data),
  createStudent: (data) => api.post('/admin/students', data).then(r => r.data),
  updateStudent: (id, data) => api.put(`/admin/students/${id}`, data).then(r => r.data),
  deleteStudent: (id) => api.delete(`/admin/students/${id}`).then(r => r.data),
};

export default adminService;
