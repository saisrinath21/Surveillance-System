import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts';
import { policeAPI } from '../services/api';

export default function PoliceDashboard({ policeId, policeCode }) {
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    // Refresh every 30 seconds
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [alertsRes, statsRes, metricsRes] = await Promise.all([
        policeAPI.getAlerts(),
        policeAPI.getAlertStats(),
        policeAPI.getResponseMetrics()
      ]);
      setAlerts(alertsRes.data);
      setStats(statsRes.data);
      setMetrics(metricsRes.data);
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRespond = async (alertId, response) => {
    try {
      await policeAPI.respondToAlert(alertId, response);
      loadData();
    } catch (err) {
      console.error('Failed to respond:', err);
    }
  };

  const handleCallUser = async (alertId) => {
    try {
      await policeAPI.callUser(alertId);
      alert('Calling user...');
    } catch (err) {
      console.error('Failed to call user:', err);
    }
  };

  const responseTimeData = [
    { name: 'Mon', avgTime: 45 },
    { name: 'Tue', avgTime: 52 },
    { name: 'Wed', avgTime: 48 },
    { name: 'Thu', avgTime: 61 },
    { name: 'Fri', avgTime: 55 },
    { name: 'Sat', avgTime: 67 },
    { name: 'Sun', avgTime: 59 }
  ];

  const statusData = [
    { name: 'Pending', value: stats?.pending_count || 0 },
    { name: 'Responded', value: stats?.responded_count || 0 },
    { name: 'Resolved', value: stats?.resolved_count || 0 },
  ];

  const COLORS = ['#DC2626', '#2563EB', '#059669'];

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Police Alert Management</h1>
            <p className="text-gray-600 mt-2">Code: {policeCode}</p>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm font-semibold">Total Alerts</p>
          <p className="text-3xl font-bold text-blue-600 mt-2">{stats?.total_count || 0}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm font-semibold">Pending</p>
          <p className="text-3xl font-bold text-red-600 mt-2">{stats?.pending_count || 0}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm font-semibold">Response Rate</p>
          <p className="text-3xl font-bold text-blue-600 mt-2">{metrics?.response_rate || '0'}%</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm font-semibold">Avg Response Time</p>
          <p className="text-3xl font-bold text-green-600 mt-2">{metrics?.avg_response_time || '0'}m</p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Alert Status */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">Alert Status</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={statusData}
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

        {/* Response Time Trends */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">Response Time Trends</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={responseTimeData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="avgTime"
                stroke="#2563EB"
                strokeWidth={2}
                name="Avg Response Time (mins)"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Alerts Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="p-6 border-b">
          <h2 className="text-xl font-bold">Active Alerts</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Alert ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">User</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Time</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody>
              {alerts.slice(0, 10).map(alert => (
                <tr key={alert.id} className="border-t hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium">#{alert.id}</td>
                  <td className="px-6 py-4 text-sm">{alert.user_name}</td>
                  <td className="px-6 py-4 text-sm">{alert.timestamp}</td>
                  <td className="px-6 py-4 text-sm">
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${
                      alert.status === 'pending' ? 'bg-red-100 text-red-800' :
                      alert.status === 'responded' ? 'bg-blue-100 text-blue-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {alert.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm space-x-2">
                    <button
                      onClick={() => handleCallUser(alert.id)}
                      className="text-blue-500 hover:underline"
                    >
                      Call
                    </button>
                    <button
                      onClick={() => handleRespond(alert.id, 'dispatched')}
                      className="text-green-500 hover:underline"
                    >
                      Dispatch
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
