import React, { FormEvent, useCallback, useMemo, useState } from "react";
import { useNavigate } from "react-router";
import { BuoyStation } from "./api";

interface LocationFormProps {
  activeStationId?: string;
  stations: Record<string, BuoyStation>;
}

const placeholderOption = "placeholder";

export const LocationForm: React.FC<LocationFormProps> = ({
  activeStationId,
  stations,
}) => {
  const navigate = useNavigate();
  const [selectedLocationId, setSelectedLocationId] = useState(
    activeStationId || placeholderOption,
  );
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newSelectedLocationId = e.target.value;
    setSelectedLocationId(newSelectedLocationId);
    setError(null);

    // Trigger form submission when a valid location is selected
    if (stations[newSelectedLocationId] && newSelectedLocationId !== placeholderOption) {
      navigate(`/forecast/${encodeURIComponent(newSelectedLocationId)}`);
    } else if (newSelectedLocationId !== placeholderOption) {
      console.error("Selected location not found");
      setError("Please select a valid location.");
    }
  };

  const groupedStations = useMemo(() => {
    const groups = [];
    const sortedStations = Object.values(stations).sort((a, b) => {
      if (a.state !== b.state) {
        return a.state.localeCompare(b.state);
      }

      return a.name.localeCompare(b.name);
    });

    let current: BuoyStation[] = [];
    for (const s of sortedStations) {
      if (current[0]?.state !== s.state) {
        current = [];
        groups.push(current);
      }

      current.push(s);
    }

    return groups;
  }, [stations]);

  return (
    <form className="location-form" id="landing-page-location-form">
      <div className="input-wrapper">
        <select
          id="location-list"
          name="location"
          value={selectedLocationId}
          onChange={handleInputChange} // Trigger submission on change
        >
          <option value={placeholderOption} disabled>
            Search or select a location
          </option>

          {groupedStations.map((g) => (
            <optgroup key={g[0].state} label={g[0].state}>
              {g.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                </option>
              ))}
            </optgroup>
          ))}
        </select>
      </div>
      {error && <p className="error-message">{error}</p>}
    </form>
  );
};
