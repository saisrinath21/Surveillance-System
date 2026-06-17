import React, { useState, useEffect } from 'react';
import { userAPI } from '../services/api';

export default function AlertDetails({ alertId, userId, onBack }) {
  const [alert, setAlert] = useState(null);
  const [loading, setLoading] = useState(true);
  const [responding, setResponding] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAlertDetails();
  }, [alertId]);

  const fetchAlertDetails = async () => {
    try {
      setLoading(true);
      const response = await userAPI.getAlertById(alertId);
      setAlert(response.data.alert);
    } catch (err) {
      console.error('Failed to fetch alert details:', err);
      setError('Failed to load alert details');
    } finally {
      setLoading(false);
    }
  };

  const handleResponse = async (response) => {
    try {
      setResponding(true);
      await userAPI.respondToAlert(alertId, response);
      // Update local state
      setAlert(prev => ({
        ...prev,
        status: 'resolved',
        user_response: response
      }));
      // Show success message and go back after 2 seconds
      setTimeout(() => {
        onBack();
      }, 1500);
    } catch (err) {
      console.error('Failed to respond to alert:', err);
      setError('Failed to submit response');
      setResponding(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 p-6 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading alert details...</p>
        </div>
      </div>
    );
  }

  if (!alert) {
    return (
      <div className="min-h-screen bg-gray-100 p-6">
        <button
          onClick={onBack}
          className="mb-4 px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
        >
          ← Back to Dashboard
        </button>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-red-500">{error || 'Alert not found'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <button
        onClick={onBack}
        className="mb-4 px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
      >
        ← Back to Dashboard
      </button>

      <div className="max-w-4xl mx-auto bg-white rounded-lg shadow overflow-hidden">
        {/* Header */}
        <div className="bg-blue-600 text-white p-6">
          <h1 className="text-3xl font-bold">Alert Details</h1>
          <p className="text-blue-100 mt-2">Alert ID: #{alert.id}</p>
        </div>

        {/* Alert Image */}
        {alert.image_url && (
          <div className="p-6 border-b">
            <h2 className="text-lg font-semibold mb-4">Captured Image</h2>
            <div className="bg-gray-100 rounded-lg overflow-hidden flex items-center justify-center max-h-96">
              <img
                src={alert.image_url}
                alt="Alert capture"
                className="max-w-full max-h-96 object-contain"
                onError={(e) => {
                  e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"%3E%3Cpath stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /%3E%3C/svg%3E';
                }}
              />
            </div>
          </div>
        )}

        {/* Alert Information */}
        <div className="p-6 border-b">
          <h2 className="text-lg font-semibold mb-4">Alert Information</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Timestamp</p>
              <p className="text-lg font-semibold">{alert.timestamp}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Status</p>
              <span className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${
                alert.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                alert.status === 'resolved' ? 'bg-green-100 text-green-800' :
                'bg-blue-100 text-blue-800'
              }`}>
                {alert.status.toUpperCase()}
              </span>
            </div>
            <div>
              <p className="text-sm text-gray-600">Police Called</p>
              <p className="text-lg font-semibold">{alert.police_called ? 'Yes' : 'No'}</p>
            </div>
            {alert.user_response && (
              <div>
                <p className="text-sm text-gray-600">Your Response</p>
                <p className="text-lg font-semibold">{alert.user_response}</p>
              </div>
            )}
          </div>
        </div>

        {/* Response Section */}
        {alert.status === 'pending' && (
          <div className="p-6 bg-gray-50 border-t">
            <h2 className="text-lg font-semibold mb-4">Your Response</h2>
            <p className="text-gray-700 mb-6">
              Please confirm if this is a genuine threat. Your response will help us improve our security system.
            </p>
            {error && (
              <div className="mb-4 p-4 bg-red-100 text-red-700 rounded">
                {error}
              </div>
            )}
            <div className="flex gap-4">
              <button
                onClick={() => handleResponse('OK')}
                disabled={responding}
                className="flex-1 px-6 py-3 bg-green-500 text-white font-semibold rounded-lg hover:bg-green-600 disabled:bg-gray-400"
              >
                {responding ? 'Submitting...' : '✗ False Alarm'}
              </button>
              <button
                onClick={() => handleResponse('NOT OK')}
                disabled={responding}
                className="flex-1 px-6 py-3 bg-red-500 text-white font-semibold rounded-lg hover:bg-red-600 disabled:bg-gray-400"
              >
                {responding ? 'Submitting...' : '✓ Genuine Threat'}
              </button>
            </div>
          </div>
        )}

        {/* Already Responded */}
        {alert.status === 'resolved' && (
          <div className="p-6 bg-green-50 border-t border-green-200">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-green-800">You have already responded to this alert with: <span className="font-semibold">{alert.user_response}</span></p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
