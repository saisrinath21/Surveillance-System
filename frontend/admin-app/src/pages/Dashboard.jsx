import React, { useEffect, useState } from 'react';
import { adminAPI } from '../services/api';
import LocationMap from '../components/LocationMap';

export default function AdminDashboard() {
  const [stations, setStations] = useState([]);
  const [registerForm, setRegisterForm] = useState({
    token: '',
    code: '',
    password: '',
    confirmPassword: '',
    phone: '',
    latitude: '',
    longitude: ''
  });
  const [registerStatus, setRegisterStatus] = useState('ready');
  const [error, setError] = useState('');
  const [registerError, setRegisterError] = useState('');

  useEffect(() => {
    loadStations();
  }, []);

  const loadStations = async () => {
    try {
      const response = await adminAPI.getPoliceStations();
      setStations(response.data.stations || []);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load stations');
    }
  };

  const handleRegisterChange = (event) => {
    const { name, value } = event.target;
    setRegisterForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleLocationSelect = (lat, lng) => {
    setRegisterForm((prev) => ({ 
      ...prev, 
      latitude: lat.toString(), 
      longitude: lng.toString() 
    }));
  };

  const handleRegisterSubmit = async (event) => {
    event.preventDefault();
    setRegisterError('');
    setRegisterStatus('sending');

    if (registerForm.password !== registerForm.confirmPassword) {
      setRegisterError('Passwords do not match');
      setRegisterStatus('error');
      return;
    }

    try {
      const { confirmPassword, ...payload } = registerForm;
      await adminAPI.registerPoliceStation(payload);
      setRegisterStatus('sent');
      setRegisterForm({ token: '', code: '', password: '', confirmPassword: '', phone: '', latitude: '', longitude: '' });
      loadStations();
    } catch (err) {
      setRegisterError(err.response?.data?.error || 'Failed to register station');
      setRegisterStatus('error');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <h1 className="text-3xl font-bold text-slate-900">Admin dashboard</h1>
          <p className="mt-2 text-slate-600">Register police stations and review active station list.</p>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Register a police station</h2>
            <form onSubmit={handleRegisterSubmit}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-700 mb-2">Admin token</label>
                <input
                  name="token"
                  className="w-full rounded border border-slate-300 p-3"
                  value={registerForm.token}
                  onChange={handleRegisterChange}
                  required
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-700 mb-2">Police code</label>
                <input
                  name="code"
                  className="w-full rounded border border-slate-300 p-3"
                  value={registerForm.code}
                  onChange={handleRegisterChange}
                  required
                />
              </div>
              <div className="mb-4 grid gap-4 lg:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Password</label>
                  <input
                    type="password"
                    name="password"
                    className="w-full rounded border border-slate-300 p-3"
                    value={registerForm.password}
                    onChange={handleRegisterChange}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Confirm password</label>
                  <input
                    type="password"
                    name="confirmPassword"
                    className="w-full rounded border border-slate-300 p-3"
                    value={registerForm.confirmPassword}
                    onChange={handleRegisterChange}
                    required
                  />
                </div>
              </div>
              <LocationMap 
                onLocationSelect={handleLocationSelect}
                initialLat={registerForm.latitude ? parseFloat(registerForm.latitude) : 20}
                initialLng={registerForm.longitude ? parseFloat(registerForm.longitude) : 78}
                height="350px"
              />
              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-700 mb-2">Contact phone</label>
                <input
                  name="phone"
                  className="w-full rounded border border-slate-300 p-3"
                  value={registerForm.phone}
                  onChange={handleRegisterChange}
                  required
                />
              </div>
              {registerError && <p className="text-sm text-red-600 mb-4">{registerError}</p>}
              {registerStatus === 'sent' && <p className="text-sm text-green-600 mb-4">Station registered successfully.</p>}
              <button
                type="submit"
                className="inline-flex items-center justify-center rounded bg-slate-900 px-5 py-3 text-white hover:bg-slate-800"
                disabled={registerStatus === 'sending'}
              >
                {registerStatus === 'sending' ? 'Registering…' : 'Register station'}
              </button>
            </form>
          </div>
        </div>

        <div className="mt-6 bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Registered police stations</h2>
          {stations.length === 0 ? (
            <p className="text-slate-600">No police stations are registered yet.</p>
          ) : (
            <div className="space-y-4">
              {stations.map((station) => (
                <div key={station.id} className="rounded-lg border border-slate-200 p-4">
                  <p className="font-semibold text-slate-900">{station.code}</p>
                  <p className="text-sm text-slate-600">District: {station.district}</p>
                  <p className="text-sm text-slate-600">Phone: {station.phone}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
