import React, { useState, useEffect } from 'react';
import { userAPI } from '../services/api';
import LocationMap from '../components/LocationMap';

export default function AddCamera({ userId, onBack, onCameraAdded }) {
  const [cameras, setCameras] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [editingCameraId, setEditingCameraId] = useState(null);

  // Form state
  const [formData, setFormData] = useState({
    camera_name: '',
    camera_rtsp: '',
    phone: '',
    latitude: '',
    longitude: '',
  });

  useEffect(() => {
    fetchCameras();
  }, []);

  const fetchCameras = async () => {
    try {
      setLoading(true);
      const response = await userAPI.getCameras();
      setCameras(response.data.cameras || []);
      setError(null);
    } catch (err) {
      setError('Failed to load cameras');
      console.error('Error fetching cameras:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleAddCamera = async (e) => {
    e.preventDefault();
    if (!formData.camera_name || !formData.camera_rtsp || !formData.phone || !formData.latitude || !formData.longitude) {
      setError('All fields are required');
      return;
    }

    try {
      setError(null);
      const response = await userAPI.addCamera(formData);
      setSuccess('Camera added successfully!');
      setFormData({
        camera_name: '',
        camera_rtsp: '',
        phone: '',
        latitude: '',
        longitude: '',
      });
      setShowForm(false);
      setTimeout(() => setSuccess(null), 3000);
      fetchCameras();
      if (onCameraAdded) {
        onCameraAdded();
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to add camera');
    }
  };

  const handleEditCamera = (camera) => {
    setEditingCameraId(camera.camera_id);
    setFormData({
      camera_name: camera.camera_name,
      camera_rtsp: camera.camera_url,
      phone: camera.phone,
      latitude: camera.latitude,
      longitude: camera.longitude,
    });
    setShowForm(true);
  };

  const handleUpdateCamera = async (e) => {
    e.preventDefault();
    if (!formData.camera_name || !formData.camera_rtsp || !formData.phone || !formData.latitude || !formData.longitude) {
      setError('All fields are required');
      return;
    }

    try {
      setError(null);
      await userAPI.editCameraDetails({
        camera_id: editingCameraId,
        camera_name: formData.camera_name,
        camera_url: formData.camera_rtsp,
        phone: formData.phone,
        camera_latitude: formData.latitude,
        camera_longitude: formData.longitude,
      });
      setSuccess('Camera updated successfully!');
      setFormData({
        camera_name: '',
        camera_rtsp: '',
        phone: '',
        latitude: '',
        longitude: '',
      });
      setEditingCameraId(null);
      setShowForm(false);
      setTimeout(() => setSuccess(null), 3000);
      fetchCameras();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update camera');
    }
  };

  const handleDeleteCamera = async (cameraId) => {
    if (!window.confirm('Are you sure you want to delete this camera?')) {
      return;
    }

    try {
      setError(null);
      await userAPI.deleteCamera(cameraId);
      setSuccess('Camera deleted successfully!');
      setTimeout(() => setSuccess(null), 3000);
      fetchCameras();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to delete camera');
    }
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingCameraId(null);
    setFormData({
      camera_name: '',
      camera_rtsp: '',
      phone: '',
      latitude: '',
      longitude: '',
    });
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">Manage Cameras</h1>
          <button
            onClick={onBack}
            className="px-4 py-2 text-gray-600 bg-gray-200 rounded hover:bg-gray-300 transition-colors"
          >
            Back to Dashboard
          </button>
        </div>

        {/* Messages */}
        {error && (
          <div className="mb-4 p-4 bg-red-100 text-red-800 rounded">
            {error}
          </div>
        )}
        {success && (
          <div className="mb-4 p-4 bg-green-100 text-green-800 rounded">
            {success}
          </div>
        )}

        {/* Add/Edit Camera Form */}
        {showForm && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-bold mb-4">
              {editingCameraId ? 'Edit Camera' : 'Add New Camera'}
            </h2>
            <form onSubmit={editingCameraId ? handleUpdateCamera : handleAddCamera}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Camera Name
                  </label>
                  <input
                    type="text"
                    name="camera_name"
                    value={formData.camera_name}
                    onChange={handleFormChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500"
                    placeholder="e.g., Front Door"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    RTSP URL
                  </label>
                  <input
                    type="text"
                    name="camera_rtsp"
                    value={formData.camera_rtsp}
                    onChange={handleFormChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500"
                    placeholder="e.g., rtsp://192.168.1.100/stream"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Phone Number
                  </label>
                  <input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleFormChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500"
                    placeholder="e.g., +1234567890"
                  />
                </div>
              </div>

                {/* Location Map - Full Width */}
              <div className="mt-6">
                <LocationMap
                  onLocationSelect={(lat, lng) => {
                    setFormData(prev => ({
                      ...prev,
                      latitude: lat.toString(),
                      longitude: lng.toString()
                    }));
                  }}
                  initialLat={formData.latitude ? parseFloat(formData.latitude) : 20}
                  initialLng={formData.longitude ? parseFloat(formData.longitude) : 78}
                  height="400px"
                />
              </div>

              <div className="mt-6 flex gap-3">
                <button
                  type="submit"
                  className="px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
                >
                  {editingCameraId ? 'Update Camera' : 'Add Camera'}
                </button>
                <button
                  type="button"
                  onClick={handleCancel}
                  className="px-6 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Add Camera Button */}
        {!showForm && (
          <button
            onClick={() => setShowForm(true)}
            className="w-full py-12 border-2 border-dashed border-blue-400 rounded-lg text-center mb-6 hover:bg-blue-50 transition-colors"
          >
            <div className="text-4xl text-blue-500 mb-2">+</div>
            <div className="text-lg font-semibold text-blue-600">Add Camera</div>
          </button>
        )}

        {/* Cameras List */}
        {loading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading cameras...</p>
          </div>
        ) : cameras.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <p className="text-gray-600">No cameras added yet. Click the button above to add one.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {cameras.map(camera => (
              <div
                key={camera.camera_id}
                className={`rounded-lg shadow p-6 transition-all ${
                  camera.model_active
                    ? 'bg-green-100 border-l-4 border-green-500'
                    : 'bg-red-100 border-l-4 border-red-500'
                }`}
              >
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h3 className="text-lg font-bold text-gray-800">{camera.camera_name}</h3>
                    <p className="text-sm text-gray-600">
                      {camera.model_active ? '🟢 Running' : '🔴 Inactive'}
                    </p>
                  </div>
                </div>

                <div className="text-sm text-gray-700 space-y-1 mb-4">
                  <p><strong>URL:</strong> {camera.camera_url}</p>
                  <p><strong>Phone:</strong> {camera.phone}</p>
                  <p><strong>Location:</strong> ({camera.latitude}, {camera.longitude})</p>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => handleEditCamera(camera)}
                    className="flex-1 px-3 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm transition-colors"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDeleteCamera(camera.camera_id)}
                    className="flex-1 px-3 py-2 bg-red-500 text-white rounded hover:bg-red-600 text-sm transition-colors"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
