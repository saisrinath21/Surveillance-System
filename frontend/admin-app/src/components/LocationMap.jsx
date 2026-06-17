import React, { useState, useEffect } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix leaflet default icon issue with Parcel/Vite
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

export default function LocationMap({ onLocationSelect, initialLat, initialLng, height = '400px' }) {
  const [map, setMap] = useState(null);
  const [marker, setMarker] = useState(null);
  const [selectedLat, setSelectedLat] = useState(initialLat || 0);
  const [selectedLng, setSelectedLng] = useState(initialLng || 0);

  // Initialize map
  useEffect(() => {
    if (map) return;

    const mapContainer = document.getElementById('map-container');
    if (!mapContainer) return;

    const newMap = L.map('map-container').setView(
      [initialLat || 20, initialLng || 78],
      5
    );

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
      maxZoom: 19,
    }).addTo(newMap);

    // Add click handler to map
    newMap.on('click', (e) => {
      const { lat, lng } = e.latlng;
      setSelectedLat(lat);
      setSelectedLng(lng);

      // Update or create marker
      if (marker) {
        marker.setLatLng([lat, lng]);
      } else {
        const newMarker = L.marker([lat, lng]).addTo(newMap);
        setMarker(newMarker);
      }

      // Call callback
      if (onLocationSelect) {
        onLocationSelect(lat, lng);
      }
    });

    // Add initial marker if coordinates provided
    if (initialLat && initialLng) {
      const initialMarker = L.marker([initialLat, initialLng]).addTo(newMap);
      setMarker(initialMarker);
    }

    setMap(newMap);

    return () => {
      newMap.remove();
    };
  }, []);

  return (
    <div className="mb-4">
      <label className="block text-sm font-medium text-gray-700 mb-2">
        Select Location (Click on Map)
      </label>
      <div
        id="map-container"
        style={{ height, width: '100%', borderRadius: '0.375rem', border: '1px solid #d1d5db' }}
      ></div>
      <div className="mt-3 p-3 bg-blue-50 rounded text-sm text-gray-700">
        <p>
          <strong>Selected Coordinates:</strong>
        </p>
        <p>Latitude: {selectedLat.toFixed(6)}</p>
        <p>Longitude: {selectedLng.toFixed(6)}</p>
      </div>
    </div>
  );
}
