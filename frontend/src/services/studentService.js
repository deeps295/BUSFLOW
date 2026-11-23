import api from './api';

export const studentService = {
  getRoutes: () => api.get('/student/routes').then(r => r.data),
  getSchedules: (routeId) => api.get(`/student/schedules?route_id=${routeId}`).then(r => r.data),
  getPrediction: (routeId, stopId, trafficOverride = null) => {
    let url = `/student/prediction?route_id=${routeId}&stop_id=${stopId}`;
    if (trafficOverride) url += `&traffic_override=${trafficOverride}`;
    return api.get(url).then(r => r.data);
  },
  getTripStatus: (routeId) => api.get(`/student/trip-status?route_id=${routeId}`).then(r => r.data),
  getRouteStats: (routeId) => api.get(`/student/route-stats?route_id=${routeId}`).then(r => r.data),
};

export default studentService;
