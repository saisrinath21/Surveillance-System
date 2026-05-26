import React, { useState, useEffect } from 'react';
import NotificationService from '../services/NotificationService';

const notificationService = new NotificationService();

export default function Notifications({ userId }) {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    const unsubscribe = notificationService.subscribe(handleNewNotification);
    return () => unsubscribe();
  }, []);

  const handleNewNotification = (data) => {
    setNotifications(prev => [data, ...prev].slice(0, 50));
    setUnreadCount(prev => prev + 1);
  };

  const markAsRead = () => {
    setUnreadCount(0);
  };

  return (
    <div className="relative">
      <button
        onClick={markAsRead}
        className="relative inline-flex items-center p-2 text-gray-600 hover:text-gray-900"
      >
        <svg
          className="w-6 h-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
          />
        </svg>
        {unreadCount > 0 && (
          <span className="absolute top-1 right-1 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 bg-red-600 rounded-full">
            {unreadCount}
          </span>
        )}
      </button>

      {/* Notification Dropdown */}
      <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg p-4 max-h-96 overflow-y-auto hidden group-hover:block">
        <h3 className="font-bold text-lg mb-4">Notifications</h3>
        {notifications.length === 0 ? (
          <p className="text-gray-500 text-sm">No notifications</p>
        ) : (
          notifications.map((notif, index) => (
            <div
              key={index}
              className="border-b pb-3 mb-3 last:border-b-0 last:mb-0"
            >
              <p className="font-semibold text-sm text-gray-800">{notif.title}</p>
              <p className="text-xs text-gray-600 mt-1">{notif.message}</p>
              <p className="text-xs text-gray-400 mt-1">{notif.timestamp}</p> 
            </div>
          ))
        )}
      </div>
    </div>
  );
}
