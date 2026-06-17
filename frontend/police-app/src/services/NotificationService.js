import { io } from 'socket.io-client';

class NotificationService {
  constructor(baseUrl = 'http://localhost:8080') {
    this.baseUrl = baseUrl;
    this.socket = null;
    this.listeners = [];
    this.isConnected = false;
  }

  connect() {
    const token = localStorage.getItem('token');
    if (!token) {
      return Promise.reject(new Error('No auth token available'));
    }

    return new Promise((resolve, reject) => {
      if (this.socket && this.isConnected) {
        resolve();
        return;
      }

      this.socket = io(this.baseUrl, {
        auth: { token },
        reconnection: true,
        reconnectionAttempts: 5,
        reconnectionDelay: 1000,
      });

      this.socket.on('connect', () => {
        this.isConnected = true;
        console.log('Socket.IO connected', this.socket.id);
        resolve();
      });

      this.socket.on('connect_error', (error) => {
        console.error('Socket.IO connection error:', error);
        reject(error);
      });

      this.socket.on('reconnect_attempt', (attempt) => {
        console.log(`Socket.IO reconnect attempt ${attempt}`);
      });

      this.socket.on('alert_update', (data) => {
        console.log('Socket.IO alert_update received:', data);
        this.notify({ type: 'alert', payload: data });
      });

      this.socket.on('disconnect', () => {
        this.isConnected = false;
        console.log('Socket.IO disconnected');
      });
    });
  }

  subscribe(callback) {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter(listener => listener !== callback);
    };
  }

  notify(data) {
    this.listeners.forEach(callback => callback(data));
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.isConnected = false;
    }
  }
}

export default new NotificationService();
