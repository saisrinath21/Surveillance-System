import axios from 'axios';

const API_BASE_URL = 'http://localhost:8080';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Add token to request headers
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle token expiration - do NOT redirect, let app handle it
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Dispatch custom event instead of redirecting
      window.dispatchEvent(new Event('token-expired'));
    }
    return Promise.reject(error);
  }
);

export const policeAPI = {
  login: (data) => api.post('/police-login', data),
  logout: () => api.post('/logout'),
  getAlerts: () => api.get('/get-police-alerts'),
  getAlertStats: () => api.get('/police-alert-stats'),
  getResponseMetrics: () => api.get('/police-response-metrics'),
  resolveAlert: (alertId, status) => api.post(`/police-update-alert/${alertId}`, { status }),
  callUser: (alertId) => api.post(`/police-call-user/${alertId}`),
  getAlertById: (alertId) => api.get(`/alert/${alertId}`),
};

export default api;
