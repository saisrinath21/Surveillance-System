# Quick Start Guide - React Frontend

## 🚀 Fast Setup

### 1. Install Dependencies

**User App:**
```bash
cd frontend/user-app
npm install
```

**Police App:**
```bash
cd frontend/police-app
npm install
```

### 2. Start Development Servers

**Terminal 1 - User App:**
```bash
cd frontend/user-app
npm run dev
```
→ Opens at http://localhost:3000

**Terminal 2 - Police App:**
```bash
cd frontend/police-app
npm run dev
```
→ Opens at http://localhost:3001

**Terminal 3 - Backend (if not running):**
```bash
cd backend
python app.py
```

## 📋 What's Included

### User App (3000)
✅ Registration & Login
✅ Real-time Alert Dashboard
✅ Alert History & Statistics
✅ Detection Toggle
✅ Live Notifications (WebSocket)
✅ Charts (Pie, Timeline)
✅ Responsive UI (Tailwind CSS)

### Police App (3001)
✅ Officer Registration & Login
✅ Active Alerts Dashboard
✅ Response Metrics & Analytics
✅ Response Time Trends
✅ Call & Dispatch Actions
✅ Live Alert Notifications
✅ Status Charts & Analytics
✅ Professional Dark UI

## 🛠️ Technologies

- **React 18** - Modern UI library
- **Vite** - Lightning-fast build tool
- **Tailwind CSS** - Utility-first styling
- **Recharts** - Beautiful data visualizations
- **Axios** - API client
- **WebSocket** - Real-time notifications

## 📦 Project Structure

```
frontend/
├── user-app/
│   ├── src/
│   │   ├── pages/ (Login, Register, Dashboard)
│   │   ├── components/ (Notifications)
│   │   └── services/ (API, WebSocket)
│   └── vite.config.js
│
├── police-app/
│   ├── src/
│   │   ├── pages/ (Login, Register, Dashboard)
│   │   ├── components/ (Notifications)
│   │   └── services/ (API, WebSocket)
│   └── vite.config.js
│
└── README.md (Full documentation)
```

## 🔌 API Proxy

Both apps proxy requests to `http://localhost:5000`:
- Configured in `vite.config.js`
- Handles CORS automatically
- WebSocket connection: `ws://localhost:5000/ws`

## 🎨 Customization

### Change Colors
Edit `tailwind.config.js`:
```javascript
colors: {
  primary: '#YOUR_COLOR',
  secondary: '#YOUR_COLOR',
  danger: '#YOUR_COLOR',
}
```

### Add More Pages
Create components in `src/pages/` and add routes in `App.jsx`

### Modify Charts
Edit `src/pages/Dashboard.jsx` - uses Recharts components

## ✨ Features

### Real-time Notifications
- WebSocket connection with auto-reconnect
- Listener pattern for event handling
- Automatic reconnection after 3 seconds if disconnected

### Charts & Visualizations
- Pie charts for alert status
- Line charts for trends
- Bar charts for comparisons
- Fully responsive

### Authentication
- Registration & Login pages
- Session storage
- Protected dashboards
- Logout functionality

## 🚀 Next Steps

1. ✅ Install & run both apps
2. ✅ Test login/registration
3. ✅ Check WebSocket connection in browser console
4. ✅ Update API endpoints if needed
5. ✅ Customize colors and branding

## ⚠️ Troubleshooting

**Port in use?** → Change port in `vite.config.js`
**WebSocket error?** → Ensure backend is running
**CORS issue?** → Check proxy settings in `vite.config.js`
**Module not found?** → Run `npm install` again

## 📚 More Info

See `frontend/README.md` for:
- Detailed API endpoints
- WebSocket usage
- Environment variables
- Project structure
- Future enhancements

---

Ready to build? Run the setup above! 🎉
