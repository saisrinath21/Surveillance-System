import axios from 'axios';
// import { io} from 'socket.io-client';

// const socket = io('http://localhost:8080');
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

// // Add token to request headers for Socket.IO connections
// socket.on('connect', () => {
//   const token = localStorage.getItem('token');
//   if (token) {
//     socket.emit('authenticate', { token });
//   }
// });

// // Handle token expiration - do NOT redirect, let app handle it
// socket.on('unauthorized', (msg) => {
//   if (msg.data === 'Token expired') {
//     window.dispatchEvent(new Event('token-expired'));
//   }
// });

export const userAPI = {
  register: (data) => api.post('/register', data),
  login: (data) => api.post('/login', data),
  logout: () => api.post('/logout'),
  getAlerts: () => api.get('/get-alerts'),
  getAlertById: (alertId) => api.get(`/alert/${alertId}`), 
  generateOTP: (userId) => api.get(`/generate-otp/${userId}`),
  verifyOTP: (userId, otp) => api.post(`/verify-otp/${userId}?otp=${otp}`),
  respondToAlert: (alertId, response) => 
    api.post(`/update-alert-response/${alertId}`, { response }),
  getProfile: () => api.get('/user-profile'),
  updateProfile: (data) => api.put('/update-profile', data),
  toggleDetection: (status) => api.post('/toggle-detection', { status: status}),
  getDetectionStatus: () => api.get('/detection-status'),
};

export default api;
