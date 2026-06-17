import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts';
import { policeAPI } from '../services/api';
import notificationService from '../services/NotificationService';

export default function PoliceDashboard({ policeId, policeCode }) {
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState({ total_count: 0, pending_count: 0, responded_count: 0, resolved_count: 0 });
  const [metrics, setMetrics] = useState({ response_rate: 0, avg_response_time: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (localStorage.getItem('token')) {
      loadData();
      notificationService.connect().catch(err => console.error('Socket connect failed', err));
      const unsubscribe = notificationService.subscribe(handleSocketEvent);
      return () => {
        unsubscribe();
        notificationService.disconnect();
      };
    }
  }, []);

  const handleSocketEvent = (event) => {
    const payload = event.payload || event;
    console.log('Police dashboard socket event:', payload);
    if (!payload || !payload.alert_id) {
      return;
    }

    setAlerts(prevAlerts => {
      const existingIndex = prevAlerts.findIndex(item => item.alert_id === payload.alert_id);
      // If alert exists, update it and adjust stats if status changed
      if (existingIndex >= 0) {
        const oldStatus = prevAlerts[existingIndex].status;
        const newAlerts = prevAlerts.map(item => item.alert_id === payload.alert_id ? { ...item, ...payload } : item);
        if (oldStatus !== payload.status) {
          setStats(prev => {
            const s = { ...prev };
            // decrement old bucket
            if (oldStatus === 'pending') s.pending_count = Math.max(0, (s.pending_count || 0) - 1);
            else if (oldStatus === 'responded' || oldStatus === 'dispatched') s.responded_count = Math.max(0, (s.responded_count || 0) - 1);
            else if (oldStatus === 'resolved') s.resolved_count = Math.max(0, (s.resolved_count || 0) - 1);

            // increment new bucket
            if (payload.status === 'pending' || payload.status === 'escalated') s.pending_count = (s.pending_count || 0) + 1;
            else if (payload.status === 'responded' || payload.status === 'dispatched') s.responded_count = (s.responded_count || 0) + 1;
            else if (payload.status === 'resolved') s.resolved_count = (s.resolved_count || 0) + 1;

            return s;
          });
        }
        return newAlerts;
      }

      // New alert: prepend and increment totals
      setStats(prev => {
        const s = { ...prev };
        s.total_count = (s.total_count || 0) + 1;
        if (payload.status === 'pending' || payload.status === 'escalated') s.pending_count = (s.pending_count || 0) + 1;
        else if (payload.status === 'responded' || payload.status === 'dispatched') s.responded_count = (s.responded_count || 0) + 1;
        else if (payload.status === 'resolved') s.resolved_count = (s.resolved_count || 0) + 1;
        return s;
      });

      return [payload, ...prevAlerts];
    });
  };

  const loadData = async () => {
    try {
      const [alertsRes, statsRes, metricsRes] = await Promise.all([
        policeAPI.getAlerts(),
        policeAPI.getAlertStats(),
        policeAPI.getResponseMetrics()
      ]);
      setAlerts(alertsRes.data.alerts || []);
      setStats(statsRes.data || {});
      setMetrics(metricsRes.data || {});
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRespond = async (alertId, status) => {
    try {
      await policeAPI.resolveAlert(alertId, status);
      loadData();
    } catch (err) {
      console.error('Failed to update alert status:', err);
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

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading police dashboard...</p>
        </div>
      </div>
    );
  }

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
              {alerts.length === 0 ? (
                <tr>
                  <td colSpan="5" className="px-6 py-8 text-center text-gray-500">
                    No alerts assigned to your station yet.
                  </td>
                </tr>
              ) : (
                alerts.slice(0, 10).map(alert => (
                  <tr key={alert.alert_id} className="border-t hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm font-medium">#{alert.alert_id}</td>
                    <td className="px-6 py-4 text-sm">{alert.user_name || alert.user_phone || 'Unknown'}</td>
                    <td className="px-6 py-4 text-sm">{new Date(alert.timestamp).toLocaleString()}</td>
                    <td className="px-6 py-4 text-sm">
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${
                        alert.status === 'pending' ? 'bg-red-100 text-red-800' :
                        alert.status === 'responded' ? 'bg-blue-100 text-blue-800' :
                        alert.status === 'resolved' ? 'bg-green-100 text-green-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {alert.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm space-x-2">
                      <button
                        onClick={() => handleCallUser(alert.alert_id)}
                        className="text-blue-500 hover:underline"
                      >
                        Call
                      </button>
                      <button
                        onClick={() => handleRespond(alert.alert_id, 'responded')}
                        className="text-green-500 hover:underline"
                      >
                        Dispatch
                      </button>
                      {alert.status !== 'resolved' && (
                        <button
                          onClick={() => handleRespond(alert.alert_id, 'resolved')}
                          className="text-emerald-500 hover:underline"
                        >
                          Resolve
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
