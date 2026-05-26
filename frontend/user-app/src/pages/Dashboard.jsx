import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts';
import {userAPI} from '../services/api';

export default function Dashboard({ userId, username, onViewAlertDetails, onEditProfile }) {
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [detectionActive, setDetectionActive] = useState(false);

  useEffect(() => {
    
    loadAlerts();
    fetchDetectionStatus();
    setInterval(() => {
      loadAlerts();
      fetchDetectionStatus();
    }, 10000); // Refresh every 30 seconds
  }, []);

  const fetchDetectionStatus = async () => {
    try {
      const response = await userAPI.getDetectionStatus();
      setDetectionActive(response.data.model_running);
    } catch (err) {
      console.error('Failed to fetch detection status:', err);
    }
  };

  const loadAlerts = async () => {
    try {
      const response = await userAPI.getAlerts(); 
      const alertsArray = response.data.alerts || [];
      setAlerts(alertsArray);
      calculateStats(alertsArray);
    } catch (err) {
      console.error('Failed to load alerts:', err);
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (alertsList) => {
    const stats = {
      total: alertsList.length,
      pending: alertsList.filter(a => a.status === 'pending').length,
      resolved: alertsList.filter(a => a.status === 'resolved').length,
      responded: alertsList.filter(a => a.status === 'responded').length,
    };
    setStats(stats);
  };

  const toggleDetection = async () => {
    try {
      const newStatus = !detectionActive;
      await userAPI.toggleDetection(newStatus);
      setDetectionActive(newStatus);
    } catch (err) {
      console.error('Failed to toggle detection:', err);
    }
  };

  const chartData = [
    { name: 'Pending', value: stats?.pending || 0 },
    { name: 'Resolved', value: stats?.resolved || 0 },
    { name: 'Responded', value: stats?.responded || 0 },
  ];

  const COLORS = ['#F59E0B', '#10B981', '#3B82F6'];

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold">Welcome, {username}!</h1>
            <button
              id="edit-profile-btn"
              onClick={onEditProfile}
              className="p-2 rounded-full hover:bg-blue-50 text-gray-400 hover:text-blue-600 transition-all duration-200 group relative"
              title="Edit Profile"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
              </svg>
              <span className="absolute -bottom-8 left-1/2 -translate-x-1/2 bg-gray-800 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
                Edit Profile
              </span>
            </button>
            <p className="text-gray-600 mt-2 hidden md:block">Monitor your surveillance system</p>
          </div>
          <button
            onClick={toggleDetection}
            className={`px-6 py-2 rounded-lg text-white font-semibold ${
              (detectionActive) ? 'bg-green-500 hover:bg-green-600' : 'bg-red-500 hover:bg-red-600'
            }`}
          >
            Detection: {(detectionActive) ? 'ON' : 'OFF'}
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm font-semibold">Total Alerts</p>
          <p className="text-3xl font-bold text-blue-500 mt-2">{stats?.total || 0}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm font-semibold">Pending</p>
          <p className="text-3xl font-bold text-yellow-500 mt-2">{stats?.pending || 0}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm font-semibold">Resolved</p>
          <p className="text-3xl font-bold text-green-500 mt-2">{stats?.resolved || 0}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm font-semibold">Responded</p>
          <p className="text-3xl font-bold text-blue-500 mt-2">{stats?.responded || 0}</p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Alert Status Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">Alert Status Distribution</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {COLORS.map((color, index) => (
                  <Cell key={`cell-${index}`} fill={color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Alerts Timeline */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">Recent Activity</h2>
          <div className="space-y-3">
            {alerts.slice(0, 5).map(alert => (
              <div key={alert.alert_id} className="border-l-4 border-blue-500 pl-4 py-2">
                <p className="font-semibold text-gray-800">Alert #{alert.alert_id}</p>
                <p className="text-sm text-gray-600">{alert.timestamp}</p>
                <span className={`inline-block mt-1 px-2 py-1 rounded text-xs font-semibold ${
                  alert.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                  alert.status === 'resolved' ? 'bg-green-100 text-green-800' :
                  'bg-blue-100 text-blue-800'
                }`}>
                  {alert.status.toUpperCase()}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Alerts Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="p-6 border-b">
          <h2 className="text-xl font-bold">All Alerts</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Time</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Response</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Action</th>
              </tr>
            </thead>
            <tbody>
              {alerts.map(alert => (
                <tr key={alert.alert_id} className="border-t hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium">#{alert.alert_id}</td>
                  <td className="px-6 py-4 text-sm">{alert.timestamp}</td>
                  <td className="px-6 py-4 text-sm">
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${
                      alert.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                      alert.status === 'resolved' ? 'bg-green-100 text-green-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {alert.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm">{alert.user_response || '-'}</td>
                  <td className="px-6 py-4 text-sm">
                    <button 
                      className="text-blue-500 hover:underline"
                      onClick={() => onViewAlertDetails(alert.alert_id)}
                    >
                      View Details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
