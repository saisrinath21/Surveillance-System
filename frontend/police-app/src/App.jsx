import React, { useState, useEffect } from 'react';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import Dashboard from './pages/Dashboard';
import Notifications from './components/Notifications';
import { policeAPI } from './services/api';
import './index.css';

export default function App() {
  const [currentPage, setCurrentPage] = useState('login');
  const [police, setPolice] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if police officer is already logged in
    const token = localStorage.getItem('token');
    const policeId = localStorage.getItem('policeId');
    const policeCode = localStorage.getItem('policeCode');
    
    if (token && policeId && policeCode) {
      setPolice({ id: policeId, code: policeCode });
      setCurrentPage('dashboard');
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    // Listen for token expiration event
    const handleTokenExpired = () => {
      localStorage.removeItem('token');
      localStorage.removeItem('policeId');
      localStorage.removeItem('policeCode');
      setPolice(null);
      setCurrentPage('login');
    };

    window.addEventListener('token-expired', handleTokenExpired);
    return () => window.removeEventListener('token-expired', handleTokenExpired);
  }, []);

  const handleLoginSuccess = (policeData) => {
    setPolice(policeData);
    setCurrentPage('dashboard');
  };

  const handleRegisterSuccess = () => {
    setCurrentPage('login');
  };

  const handleLogout = async () => {
    try {
      await policeAPI.logout();
    } catch (err) {
      console.error('Logout failed:', err);
    } finally {
      // Always clear local data
      localStorage.removeItem('token');
      localStorage.removeItem('policeId');
      localStorage.removeItem('policeCode');
      setPolice(null);
      setCurrentPage('login');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      {police ? (
        <>
          {/* Navigation Bar */}
          <nav className="bg-white shadow border-b-4 border-red-600">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between items-center h-16">
                <div className="flex items-center">
                  <span className="text-xl font-bold text-red-600">Police Alert System</span>
                </div>
                <div className="flex items-center space-x-4">
                  <Notifications />
                  <button
                    onClick={handleLogout}
                    className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded hover:bg-red-700"
                  >
                    Logout
                  </button>
                </div>
              </div>
            </div>
          </nav>

          {/* Main Content */}
          <Dashboard policeId={police.id} policeCode={police.code} />
        </>
      ) : currentPage === 'login' ? (
        <>
          <PoliceLoginPage onLoginSuccess={handleLoginSuccess} />
          <div className="text-center py-4">
            <button
              onClick={() => setCurrentPage('register')}
              className="text-red-500 hover:underline"
            >
              New officer? Register
            </button>
          </div>
        </>
      ) : (
        <>
          <RegisterPage onRegisterSuccess={handleRegisterSuccess} />
          <div className="text-center py-4">
            <button
              onClick={() => setCurrentPage('login')}
              className="text-red-500 hover:underline"
            >
              Already registered? Login
            </button>
          </div>
        </>
      )}
    </>
  );
}

function PoliceLoginPage({ onLoginSuccess }) {
  return <LoginPage onLoginSuccess={onLoginSuccess} />;
}
