'use client';

import React, { useEffect, useState } from 'react';
import LocationForm from './LocationForm';
import '@/styles/globals.css';
import dynamic from 'next/dynamic';

// Dynamically import the MapComponent and disable SSR
const MapComponent = dynamic(() => import('./MapComponent'), { ssr: false });

// Define the interface for BuoyStation
interface BuoyStation {
  latitude: number;
  longitude: number;
  name: string;
}

const Page: React.FC = () => {
  // State to store the fetched station data
  const [stations, setStations] = useState<Record<string, BuoyStation>>({});
  const [loading, setLoading] = useState<boolean>(true);  // To handle loading state
  const [error, setError] = useState<string | null>(null); // To handle errors

  // Fetch station data from the Starlette API when the component loads
  useEffect(() => {
    const fetchStations = async () => {
      try {
        const response = await fetch('/api/locations');  // Adjust the URL if necessary
        if (!response.ok) {
          throw new Error('Failed to fetch station data');
        }
        const data = await response.json();
        setStations(data?.locations || {});  // Set the fetched stations into state
        setLoading(false);   // Set loading to false once data is loaded
      } catch (error) {
        console.error('Error fetching station data:', error);
        setError('Failed to fetch station data');
        setLoading(false);
      }
    };

    fetchStations(); // Call the fetch function
  }, []); // Empty dependency array to run this effect only once when the component mounts

  if (loading) {
    return <p>Loading map...</p>;  // Show loading message while data is being fetched
  }

  if (error) {
    return <p>{error}</p>;  // Show error message if there is a problem with fetching
  }

  return (
    <div className="landing_page">
      <div id="main-container">
        <div id="header">
          <p className="landing_page_title">Surf Forecast</p>

          <LocationForm stations={stations} />

        </div>
        <MapComponent stations={stations} />
      </div>
    </div>
  );
};

export default Page;
