"use client";

import React, { useState, FormEvent } from 'react';
import { useRouter } from 'next/navigation';

interface BuoyStation {
  latitude: number;
  longitude: number;
  name: string;
}

interface MapComponentProps {
  stations: { [key: string]: BuoyStation };
}

const LocationForm: React.FC<MapComponentProps> = ({stations}) => {
  const router = useRouter();
  const [location, setLocation] = useState('');

  const [error, setError] = useState<string | null>(null);

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    // Find the selected location ID based on the name entered
    const selectedLocationId = Object.entries(stations).find(
      ([_, loc]) => loc.name === location
    )?.[0];

    if (selectedLocationId) {
      // Navigate to the forecast page using the location_id as a path parameter
      router.push(`/forecast/${encodeURIComponent(selectedLocationId)}`);
    } else {
      // Handle case where the location is not found
      console.error('Selected location not found');
      setError('Please select a valid location.');
    }
  };

  return (
    <form
      className="location_form"
      id="landing_page_location_form"
      onSubmit={handleSubmit}
    >
      <input
        id="location_list"
        type="text"
        name="location"
        list="options"
        placeholder="Search or select a location"
        value={location}
        onChange={(e) => setLocation(e.target.value)}
      />
      <datalist id="options">
        {Object.entries(stations).map(([locId, loc]) => (
          <option key={locId} value={loc.name} data-locid={locId}>
            {loc.name}
          </option>
        ))}
      </datalist>
      <br /><br />
      <input id="submit_button" type="submit" value="Submit" />
      
      {error && <p style={{ color: 'red' }}>{error}</p>} {/* Display error message */}
    </form>
  );
};

export default LocationForm;