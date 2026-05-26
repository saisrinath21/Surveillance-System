import React, { useState, useEffect } from 'react';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import Dashboard from './pages/Dashboard';
import AlertDetails from './pages/AlertDetails';
import Notifications from './components/Notifications';
import OTPVerification from './pages/OTPVerification';
import EditProfile from './pages/EditProfile';
import { userAPI } from './services/api';
import './index.css';

export default function App() {
  const [currentPage, setCurrentPage] = useState('login');
  const [selectedAlertId, setSelectedAlertId] = useState(null);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('token');
    const userId = localStorage.getItem('userId');
    const username = localStorage.getItem('username');
    
    if (token && userId && username) {
      setUser({ id: userId, username });
      setCurrentPage('dashboard');
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    // Listen for token expiration event
    const handleTokenExpired = () => {
      localStorage.removeItem('token');
      localStorage.removeItem('userId');
      localStorage.removeItem('username');
      setUser(null);
      setCurrentPage('login');
    };

    window.addEventListener('token-expired', handleTokenExpired);
    return () => window.removeEventListener('token-expired', handleTokenExpired);
  }, []);

  const handleLoginSuccess = (userData) => {
    setUser(userData);
    setCurrentPage('dashboard');
  };

  const handleRegisterSuccess = () => {
    setCurrentPage('login');
  };

  const handleLogout = async () => {
    try {
      await userAPI.logout();
    } catch (err) {
      console.error('Logout failed:', err);
    } finally {
      // Always clear local data
      localStorage.removeItem('token');
      localStorage.removeItem('userId');
      localStorage.removeItem('username');
      setUser(null);
      setCurrentPage('login');
    }
  };

  const handleViewAlertDetails = (alertId) => {
    setSelectedAlertId(alertId);
    setCurrentPage('alert-details');
  };

  const handleBackToDashboard = () => {
    setSelectedAlertId(null);
    setCurrentPage('dashboard');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      {user ? (
        <>
          {/* Navigation Bar */}
          <nav className="bg-white shadow">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between items-center h-16">
                <div className="flex items-center">
                  <span className="text-xl font-bold text-blue-600">SurveillanceApp</span>
                </div>
                <div className="flex items-center space-x-4">
                  <Notifications userId={user.id} />
                  <button
                    onClick={() => setCurrentPage('otp-verification')}
                    className="px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded hover:bg-blue-100 transition-colors"
                  >
                    Profile
                  </button>
                  <button
                    onClick={handleLogout}
                    className="px-4 py-2 text-sm font-medium text-white bg-red-500 rounded hover:bg-red-600"
                  >
                    Logout
                  </button>
                </div>
              </div>
            </div>
          </nav>

          {/* Main Content */}
          {currentPage === 'dashboard' ? (
            <Dashboard 
              userId={user.id} 
              username={user.username}
              onViewAlertDetails={handleViewAlertDetails}
              onEditProfile={() => setCurrentPage('otp-verification')}
            />
          ) : currentPage === 'alert-details' ? (
            <AlertDetails 
              alertId={selectedAlertId}
              userId={user.id}
              onBack={handleBackToDashboard}
            />) : currentPage === 'otp-verification' ? (
            <OTPVerification 
              userId={user.id}
              onSuccess={() => setCurrentPage('edit-profile')}
              onCancel={handleBackToDashboard}
            />
          ) : currentPage === 'edit-profile' ? (
            <EditProfile 
              userId={user.id}
              onSuccess={() => setCurrentPage('dashboard')}
            />
           ) : null}
        </> 
      ) : currentPage === 'login' ? (
        <LoginPage 
          onLoginSuccess={handleLoginSuccess}
          onRegisterClick={() => setCurrentPage('register')}
        />
      ) : (
        <RegisterPage 
          onRegisterSuccess={handleRegisterSuccess}
          onLoginClick={() => setCurrentPage('login')}
        />
      )}
    </>
  );
}
