import api from './api';

export const driverService = {
  getAssignedBus: () => api.get('/driver/assigned-bus').then(r => r.data),
  startTrip: (data) => api.post('/driver/trip/start', data).then(r => r.data),
  updateTrip: (data) => api.post('/driver/trip/update', data).then(r => r.data),
  reportTraffic: (data) => api.post('/driver/traffic', data).then(r => r.data),
  completeTrip: (data) => api.post('/driver/trip/complete', data).then(r => r.data),
};

export default driverService;
