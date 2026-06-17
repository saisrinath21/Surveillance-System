Test scripts

`test_socket_delivery.js` - Node script that:
- Registers a temporary police station
- Logs in as that station to get a JWT
- Connects to the backend with Socket.IO using the JWT
- Pushes an admin alert to the station and waits for the `alert_update` event

Run:

```bash
cd <repo-root>
# install deps for this script
npm install axios socket.io-client
node scripts/test_socket_delivery.js
```

Ensure the backend is running on http://localhost:8080 before running the test.
