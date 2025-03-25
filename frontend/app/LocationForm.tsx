import React, { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router";
import { BuoyStation } from "./api";
import { useStations } from "./Stations";

interface LocationFormProps {
  activeStationId?: string;
}

export const LocationForm: React.FC<LocationFormProps> = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("");
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Ref for the dropdown to detect clicks outside
  const dropdownRef = useRef<HTMLUListElement | null>(null);

  // Filter stations based on search query, group by state
  const stations = useStations();
  const groupedStations = useMemo(() => {
    const lowercasedQuery = searchQuery.toLowerCase();
    const filteredStations = Object.values(stations).filter(
      (station) =>
        station.name.toLowerCase().includes(lowercasedQuery) ||
        station.state.toLowerCase().includes(lowercasedQuery)
    );

    const groups: Record<string, BuoyStation[]> = {};
    filteredStations.forEach((station) => {
      if (!groups[station.state]) {
        groups[station.state] = [];
      }
      groups[station.state].push(station);
    });

    return Object.entries(groups).sort(([stateA], [stateB]) =>
      stateA.localeCompare(stateB)
    );
  }, [stations, searchQuery]);

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
    setIsDropdownOpen(false); // Close the dropdown after selection
    setError(null);
    navigate(`/forecast/${encodeURIComponent(stationId)}`);
  };

  // Close dropdown if click happens outside of dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
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
