// Test script to validate police socket room delivery
// Usage: install dependencies: npm install axios socket.io-client
// Then run: node scripts/test_socket_delivery.js

const axios = require('axios');
const { io } = require('socket.io-client');

const BASE = 'http://localhost:8080';

async function main() {
  try {
    // 1) Register a temporary police station
    const code = 'test-' + Date.now();
    const password = 'testpass';
    console.log('Registering police station', code);
    await axios.post(`${BASE}/police-register`, {
      code,
      password,
      phone: '0000000000',
      address: 'Test Address'
    });

    // 2) Login as police to obtain a token
    console.log('Logging in as police');
    const login = await axios.post(`${BASE}/police-login`, { code, password });
    const token = login.data.token;
    console.log('Received token:', token ? 'YES' : 'NO');

    // 3) Connect Socket.IO client with token
    console.log('Connecting socket.io client...');
    const socket = io(BASE, { auth: { token }, transports: ['websocket'] });

    socket.on('connect', () => {
      console.log('Socket connected, id=', socket.id);
    });

    socket.on('connect_error', (err) => {
      console.error('Socket connect_error:', err.message || err);
    });

    socket.on('alert_update', (data) => {
      console.log('Received alert_update:', JSON.stringify(data, null, 2));
      cleanup(0);
    });

    // 4) Find station id
    const stationsRes = await axios.get(`${BASE}/police-stations`);
    const stations = stationsRes.data.stations || [];
    const station = stations.find(s => s.code === code) || stations[0];
    if (!station) {
      console.error('No stations available to push alert to');
      cleanup(1);
      return;
    }
    console.log('Using station:', station.id, station.code || station.address);

    // 5) Push admin alert
    console.log('Pushing admin alert to station...');
    await axios.post(`${BASE}/admin/push-police-alert`, {
      station_id: station.id,
      title: 'Automated test alert',
      message: 'This is a test pushed by test_socket_delivery.js'
    });

    // Wait up to 15s for alert
    setTimeout(() => {
      console.error('Timed out waiting for alert_update');
      cleanup(1);
    }, 15000);

    function cleanup(code) {
      try { socket.close(); } catch (e) {}
      process.exit(code);
    }

  } catch (err) {
    console.error('Test failed:', err.response?.data || err.message || err);
    process.exit(1);
  }
}

main();
