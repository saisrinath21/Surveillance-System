import React, { useState, useEffect } from 'react';
import {
  Tooltip, ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts';
import {userAPI} from '../services/api';
import notificationService from '../services/NotificationService';

export default function Dashboard({ user, onViewAlertDetails, onAddCamera }) {
  const [cameras, setCameras] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [cameraLoading, setCameraLoading] = useState(true);
  const [selectedCameraId, setSelectedCameraId] = useState(null);
  const username = user?.username || localStorage.getItem('username');

  useEffect(() => {
    if (user?.id) {
      loadCameras();
      loadAlerts();
      notificationService.connect().catch(err => console.error('Socket connect failed', err));
    }

    const unsubscribe = notificationService.subscribe((event) => {
      if (event.type === 'alert') {
        setAlerts(prevAlerts => {
          const existingIndex = prevAlerts.findIndex(a => a.alert_id === event.payload.alert_id);
          const updatedAlerts = existingIndex >= 0
            ? prevAlerts.map(a => a.alert_id === event.payload.alert_id ? event.payload : a)
            : [event.payload, ...prevAlerts];
          calculateStats(updatedAlerts);
          return updatedAlerts;
        });
      }

      if (event.type === 'camera') {
        setCameras(prevCameras => prevCameras.map(camera =>
          camera.camera_id === event.payload.camera_id
            ? { ...camera, ...event.payload }
            : camera
        ));
      }
    });

    return () => unsubscribe();
  }, [user]);

  const loadCameras = async () => {
    try {
      const response = await userAPI.getCameras();
      setCameras(response.data.cameras || []);
    } catch (err) {
      console.error('Failed to load cameras:', err);
    } finally {
      setCameraLoading(false);
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

  const handleCameraClick = (cameraId) => {
    setSelectedCameraId(cameraId);
    // Load alerts for this specific camera
  };

  const getCameraAlerts = (cameraId) => {
    return alerts.filter(a => a.camera_id === cameraId);
  };

  const toggleDetection = async (cameraId, currentStatus) => {
    try {
      await userAPI.toggleDetection(cameraId, !currentStatus);
      loadCameras();
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

  if (selectedCameraId) {
    const selectedCamera = cameras.find(c => c.camera_id === selectedCameraId);
    const cameraAlerts = getCameraAlerts(selectedCameraId);

    return (
      <div className="min-h-screen bg-gray-100 p-6">
        {/* Back Button and Header */}
        <div className="max-w-7xl mx-auto">
          <button
            onClick={() => setSelectedCameraId(null)}
            className="mb-4 px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors"
          >
            ← Back to Cameras
          </button>

          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <div className="flex justify-between items-center">
              <div>
                <h1 className="text-3xl font-bold">{selectedCamera?.camera_name}</h1>
                <p className="text-gray-600 mt-2">Camera ID: {selectedCameraId}</p>
              </div>
              <button
                onClick={() => toggleDetection(selectedCameraId, selectedCamera.model_active || false)}
                className={`px-6 py-2 rounded-lg text-white font-semibold ${
                  selectedCamera.model_active ? 'bg-green-500 hover:bg-green-600' : 'bg-red-500 hover:bg-red-600'
                }`}
              >
                Detection: {selectedCamera.model_active ? 'ON' : 'OFF'}
              </button>
            </div>
          </div>

          {/* Camera Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-gray-600 text-sm font-semibold">Total Alerts</p>
              <p className="text-3xl font-bold text-blue-500 mt-2">{cameraAlerts.length}</p>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-gray-600 text-sm font-semibold">Pending</p>
              <p className="text-3xl font-bold text-yellow-500 mt-2">
                {cameraAlerts.filter(a => a.status === 'pending').length}
              </p>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-gray-600 text-sm font-semibold">Resolved</p>
              <p className="text-3xl font-bold text-green-500 mt-2">
                {cameraAlerts.filter(a => a.status === 'resolved').length}
              </p>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-gray-600 text-sm font-semibold">Responded</p>
              <p className="text-3xl font-bold text-blue-500 mt-2">
                {cameraAlerts.filter(a => a.status === 'responded').length}
              </p>
            </div>
          </div>

          {/* Alerts Table */}
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="p-6 border-b">
              <h2 className="text-xl font-bold">Camera Alerts</h2>
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
                  {cameraAlerts.length === 0 ? (
                    <tr>
                      <td colSpan="5" className="px-6 py-4 text-center text-gray-600">
                        No alerts for this camera
                      </td>
                    </tr>
                  ) : (
                    cameraAlerts.map(alert => (
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
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold">Welcome, {username}!</h1>
              <p className="text-gray-600 mt-2 hidden md:block">Monitor your surveillance system</p>
            </div>
            <button
              onClick={onAddCamera}
              className="px-6 py-2 rounded-lg text-white font-semibold bg-blue-500 hover:bg-blue-600 transition-colors"
            >
              Add Camera
            </button>
          </div>
        </div>

        {/* Cameras Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4">Your Cameras</h2>
          {cameraLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
            </div>
          ) : cameras.length === 0 ? (
            <div className="bg-white rounded-lg shadow p-8 text-center">
              <p className="text-gray-600 mb-4">No cameras added yet</p>
              <button
                onClick={onAddCamera}
                className="px-6 py-2 rounded-lg text-white font-semibold bg-blue-500 hover:bg-blue-600 transition-colors"
              >
                Add Your First Camera
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {cameras.map(camera => (
                <div
                  key={camera.camera_id}
                  onClick={() => handleCameraClick(camera.camera_id)}
                  className={`rounded-lg shadow p-6 cursor-pointer transition-all transform hover:scale-105 ${
                    camera.model_active
                      ? 'bg-green-100 border-l-4 border-green-500'
                      : 'bg-red-100 border-l-4 border-red-500'
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="text-lg font-bold text-gray-800">{camera.camera_name}</h3>
                      <p className="text-sm text-gray-600 mt-1">
                        {camera.model_active ? '🟢 Running' : '🔴 Inactive'}
                      </p>
                    </div>
                  </div>
                  <div className="mt-3 text-sm text-gray-700">
                    <p>Alerts: {getCameraAlerts(camera.camera_id).length}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Overall Stats and Charts */}
        {cameras.length > 0 && (
          <>
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

            {/* All Alerts Table */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <div className="p-6 border-b">
                <h2 className="text-xl font-bold">All Alerts</h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">ID</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Camera</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Time</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Response</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {alerts.length === 0 ? (
                      <tr>
                        <td colSpan="6" className="px-6 py-4 text-center text-gray-600">
                          No alerts yet
                        </td>
                      </tr>
                    ) : (
                      alerts.map(alert => (
                        <tr key={alert.alert_id} className="border-t hover:bg-gray-50">
                          <td className="px-6 py-4 text-sm font-medium">#{alert.alert_id}</td>
                          <td className="px-6 py-4 text-sm">
                            {cameras.find(c => c.camera_id === alert.camera_id)?.camera_name || 'Unknown'}
                          </td>
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
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
