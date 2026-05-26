# React Frontend Setup

Two separate React applications for the Surveillance System:
- **user-app**: User monitoring interface (runs on port 3000)
- **police-app**: Police alert management interface (runs on port 3001)

## Features

### User App
- User registration and login
- Real-time alert monitoring with WebSocket notifications
- Alert statistics with Recharts visualizations
- Detection system toggle
- Alert history and status tracking
- Responsive design with Tailwind CSS

### Police App
- Police officer registration and login
- Real-time alert dashboard
- Alert status pie charts
- Response time trends analysis
- Response metrics and statistics
- Call and dispatch actions
- Responsive admin interface

## Installation

### Prerequisites
- Node.js 16+
- npm or yarn

### Setup User App

```bash
cd user-app
npm install
```

### Setup Police App

```bash
cd police-app
npm install
```

## Running the Applications

### Development Mode

**User App (Terminal 1):**
```bash
cd user-app
npm run dev
```
Access at: http://localhost:3000

**Police App (Terminal 2):**
```bash
cd police-app
npm run dev
```
Access at: http://localhost:3001

### Production Build

**User App:**
```bash
cd user-app
npm run build
```

**Police App:**
```bash
cd police-app
npm run build
```

## Technologies Used

### Frontend Stack
- **React 18** - UI framework
- **Vite** - Fast build tool
- **Tailwind CSS** - Styling
- **Recharts** - Data visualization
- **Axios** - HTTP client
- **React Router** - Navigation (ready to implement)

### Real-time Features
- **WebSocket** - Live notifications (NotificationService)
- **Auto-reconnect** - Automatic reconnection on disconnect
- **Event subscription** - Listener pattern for notifications

## Project Structure

```
user-app/
├── src/
│   ├── components/
│   │   └── Notifications.jsx
│   ├── pages/
│   │   ├── LoginPage.jsx
│   │   ├── RegisterPage.jsx
│   │   └── Dashboard.jsx
│   ├── services/
│   │   ├── api.js
│   │   └── NotificationService.js
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
└── postcss.config.js

police-app/
└── (Same structure with police-specific components)
```

## API Integration

Both apps connect to the Flask backend at `http://localhost:5000`.

### User API Endpoints
- `POST /user-register` - User registration
- `POST /user-login` - User login
- `GET /logout` - Logout
- `GET /user-alerts` - Get user alerts
- `POST /alert-response/{alertId}` - Respond to alert
- `POST /detection-toggle` - Toggle detection

### Police API Endpoints
- `POST /police-register` - Police registration
- `POST /police-login` - Police login
- `GET /police-alerts` - Get alerts
- `GET /alert-stats` - Alert statistics
- `POST /police-response/{alertId}` - Respond to alert
- `GET /response-metrics` - Response metrics
- `POST /call-user/{alertId}` - Call user
- `GET /suspicious-zones` - Get suspicious zones

## WebSocket Connection

```
ws://localhost:5000/ws?user_id={userId}
```

The WebSocket service automatically handles:
- Connection establishment
- Message parsing
- Listener notifications
- Auto-reconnection on disconnect

## Customization

### Colors
Edit `tailwind.config.js` to customize colors:

**User App Colors:**
- Primary: #3B82F6 (Blue)
- Secondary: #10B981 (Green)
- Danger: #EF4444 (Red)

**Police App Colors:**
- Primary: #2563EB (Blue)
- Secondary: #059669 (Green)
- Danger: #DC2626 (Red)
- Warning: #D97706 (Amber)

### Charts
All charts use Recharts. Customize in `Dashboard.jsx` pages.

## Environment Variables

Create `.env` file in each app if needed (for API base URLs):

```env
VITE_API_BASE_URL=http://localhost:5000
VITE_WS_BASE_URL=ws://localhost:5000
```

## Troubleshooting

### Port Already in Use
If port 3000 or 3001 is already in use, change in `vite.config.js`:
```javascript
server: {
  port: YOUR_PORT_HERE,
}
```

### WebSocket Connection Failed
Ensure the backend is running and Flask-SocketIO is configured:
```bash
cd backend
python app.py
```

### CORS Issues
The Vite proxy in `vite.config.js` forwards `/api` requests to the backend.

## Future Enhancements

- [ ] React Router for better navigation
- [ ] Redux/Context for state management
- [ ] Advanced filtering and search
- [ ] Map integration for location tracking
- [ ] Export data to CSV/PDF
- [ ] Dark mode toggle
- [ ] Multi-language support
- [ ] Progressive Web App (PWA)

## License

MIT
