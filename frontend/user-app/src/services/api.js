import axios from 'axios';
// import { io} from 'socket.io-client';

// const socket = io('http://localhost:8080');
const API_BASE_URL = 'http://localhost:8080';
const SOCKET_BASE_URL = 'http://localhost:8080';


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


export const userAPI = {
  register: (data) => api.post('/register', data),
  login: (data) => api.post('/login', data),
  logout: () => api.post('/logout'),
  getAlerts: () => api.get('/get-alerts'),
  getAlertById: (alertId) => api.get(`/alert/${alertId}`), 
  generateOTP: (userId) => api.get(`/generate-otp/${userId}`),
  verifyOTP: (userId, otp) => api.post(`/verify-otp/${userId}`, { otp: otp }),
  respondToAlert: (alertId, response) => 
    api.post(`/update-alert-response/${alertId}`, { response : response }),
  updateProfile: (data) => api.put('/update-profile', data),
  addCamera: (data) => api.post('/add-camera', data),
  getCameras: () => api.get('/get-cameras'),
  getProfile: () => api.get('/profile'),
  editCameraDetails: (data) => api.post('/edit-camera-details', data),
  deleteCamera: (cameraId) => api.delete(`/delete-camera/${cameraId}`),
  toggleDetection: (cameraId, status) => api.post('/toggle-detection', { camera_id: cameraId, status: status }),
  getDetectionStatus: (cameraId) => cameraId ? api.get(`/detection-status?camera_id=${cameraId}`) : api.get('/detection-status'),
};

export default api;
