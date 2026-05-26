class NotificationService {
  constructor(baseUrl = 'ws://localhost:5000') {
    this.baseUrl = baseUrl;
    this.ws = null;
    this.listeners = [];
    this.isConnected = false;
  }

  connect(userId) {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(`${this.baseUrl}/ws?user_id=${userId}`);

        this.ws.onopen = () => {
          this.isConnected = true;
          console.log('WebSocket connected');
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this.notify(data);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };

        this.ws.onclose = () => {
          this.isConnected = false;
          console.log('WebSocket disconnected');
          // Attempt reconnection after 3 seconds
          setTimeout(() => this.connect(userId), 3000);
        };
      } catch (error) {
        reject(error);
      }
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

  send(message) {
    if (this.isConnected && this.ws) {
      this.ws.send(JSON.stringify(message));
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

export default NotificationService;
