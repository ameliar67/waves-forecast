import React, { FormEvent, useCallback, useMemo, useState } from "react";
import { useNavigate } from "react-router";
import { BuoyStation } from "./api";

interface MapComponentProps {
  activeStationId?: string;
  stations: Record<string, BuoyStation>;
}

const placeholderOption = "placeholder";

export const LocationForm: React.FC<MapComponentProps> = ({
  activeStationId,
  stations,
}) => {
  const navigate = useNavigate();
  const [selectedLocationId, setSelectedLocationId] = useState(
    activeStationId || placeholderOption
  );
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedLocationId(e.target.value);
    setError(null);
  };

  const handleSubmit = useCallback(
    (e: FormEvent<HTMLFormElement>) => {
      e.preventDefault();

      if (stations[selectedLocationId]) {
        navigate(`/forecast/${encodeURIComponent(selectedLocationId)}`);
      } else {
        console.error("Selected location not found");
        setError("Please select a valid location.");
      }
    },
    [stations, navigate, selectedLocationId]
  );

  const groupedStations = useMemo(() => {
    const groups = [];
    const sortedStations = Object.values(stations).sort((a, b) => {
      if (a.country !== b.country) {
        return a.country.localeCompare(b.country);
      }

      return a.name.localeCompare(b.name);
    });

    let current: BuoyStation[] = [];
    for (const s of sortedStations) {
      if (current[0]?.country !== s.country) {
        current = [];
        groups.push(current);
      }

      current.push(s);
    }

    return groups;
  }, [stations]);

  return (
    <form
      className="location_form"
      id="landing_page_location_form"
      onSubmit={handleSubmit}
    >
      <div className="input-wrapper">
        <select
          id="location_list"
          name="location"
          value={selectedLocationId}
          onChange={handleInputChange}
        >
          <option value={placeholderOption} disabled>
            Search or select a location
          </option>

          {groupedStations.map((g) => (
            <optgroup key={g[0].country} label={g[0].country}>
              {g.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                </option>
              ))}
            </optgroup>
          ))}
        </select>
      </div>
      <input id="submit_button" type="submit" value="Submit" />
      {error && <p className="error-message">{error}</p>}
    </form>
  );
};
