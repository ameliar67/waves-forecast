import React, { useState, useMemo, useRef, useEffect } from "react";
import { useNavigate } from "react-router";
import { BuoyStation } from "./api";

interface LocationFormProps {
  activeStationId?: string;
  stations: Record<string, BuoyStation>;
}

const placeholderOption = "placeholder";

export const LocationForm: React.FC<LocationFormProps> = ({ activeStationId, stations }) => {
  const navigate = useNavigate();
  const [selectedLocationId, setSelectedLocationId] = useState(activeStationId || placeholderOption);
  const [searchQuery, setSearchQuery] = useState("");
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Ref for the dropdown to detect clicks outside
  const dropdownRef = useRef<HTMLUListElement | null>(null);

  // Filter the stations based on the search query
  const filteredStations = useMemo(() => {
    const lowercasedQuery = searchQuery.toLowerCase();
    return Object.values(stations).filter((station) =>
      station.name.toLowerCase().includes(lowercasedQuery) ||
      station.state.toLowerCase().includes(lowercasedQuery)
    );
  }, [stations, searchQuery]);

  // Group stations by state
  const groupedStations = useMemo(() => {
    const groups: { [state: string]: BuoyStation[] } = {};
    filteredStations.forEach((station) => {
      if (!groups[station.state]) {
        groups[station.state] = [];
      }
      groups[station.state].push(station);
    });

    return Object.entries(groups).sort(([stateA], [stateB]) =>
      stateA.localeCompare(stateB)
    );
  }, [filteredStations]);

  // Handle search input change
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  // Toggle dropdown visibility
  const toggleDropdown = () => {
    setIsDropdownOpen(!isDropdownOpen);
  };

  // Handle item selection from the dropdown
  const handleItemSelect = (stationId: string) => {
    setSelectedLocationId(stationId);
    setIsDropdownOpen(false); // Close the dropdown after selection
    setError(null);
    navigate(`/forecast/${encodeURIComponent(stationId)}`);
  };

  // Close dropdown if click happens outside of dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener("click", handleClickOutside);

    return () => {
      document.removeEventListener("click", handleClickOutside);
    };
  }, []);

  // Prevent click from propagating when clicking on the search input
  const handleSearchClick = (e: React.MouseEvent<HTMLInputElement>) => {
    e.stopPropagation();
    toggleDropdown(); // Open the dropdown when clicked
  };

  return (
    <form className="location-form" id="landing-page-location-form">
      <input
        type="text"
        placeholder="Search or select a location"
        value={searchQuery}
        onChange={handleSearchChange}
        onClick={handleSearchClick} // Prevent propagation and open dropdown
        aria-label="Search locations"
        autoComplete="off"
      />
      {isDropdownOpen && (
        <ul ref={dropdownRef} id="location-list" className="dropdown-list">
          {groupedStations.length === 0 ? (
            <li className="dropdown-item">No results found</li>
          ) : (
            groupedStations.map(([state, stationsInState]) => (
              <li key={state} className="dropdown-group">
                <strong>{state}</strong>
                <ul className="dropdown-group-list">
                  {stationsInState.map((station) => (
                    <li
                      key={station.id}
                      className="dropdown-item"
                      onClick={() => handleItemSelect(station.id)}
                    >
                      {station.name}
                    </li>
                  ))}
                </ul>
              </li>
            ))
          )}
        </ul>
      )}
      {error && <p className="error-message">{error}</p>}
    </form>
  );
};
