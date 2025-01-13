"use client";

import React, { useState, FormEvent, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router';

interface BuoyStation {
  latitude: number;
  longitude: number;
  name: string;
}

interface MapComponentProps {
  stations: { [key: string]: BuoyStation };
}

export const LocationForm: React.FC<MapComponentProps> = ({ stations }) => {
  const navigate = useNavigate();
  const locationInput = useRef<HTMLInputElement>(null!);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = useCallback((e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    // Find the selected location ID based on the name entered
    const selectedLocationId = Object.entries(stations).find(
      ([_, loc]) => loc.name === locationInput.current?.value
    )?.[0];

    if (selectedLocationId) {
      // Navigate to the forecast page using the location_id as a path parameter
      navigate(`/forecast/${encodeURIComponent(selectedLocationId)}`);
    } else {
      // Handle case where the location is not found
      console.error('Selected location not found');
      setError('Please select a valid location.');
    }
  }, [navigate]);

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
        ref={locationInput}
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
