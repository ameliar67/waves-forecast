import React, { useState, FormEvent, useCallback } from "react";
import { useNavigate } from "react-router";

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
  const [inputValue, setInputValue] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
    setError(null);
  };

  const handleClear = () => {
    setInputValue("");
    setError(null);
  };

  const handleSubmit = useCallback(
    (e: FormEvent<HTMLFormElement>) => {
      e.preventDefault();

      const selectedLocationId = Object.entries(stations).find(
        ([_, loc]) => loc.name === inputValue
      )?.[0];

      if (selectedLocationId) {
        navigate(`/forecast/${encodeURIComponent(selectedLocationId)}`);
      } else {
        console.error("Selected location not found");
        setError("Please select a valid location.");
      }
    },
    [stations, navigate, inputValue]
  );

  return (
    <form
      className="location_form"
      id="landing_page_location_form"
      onSubmit={handleSubmit}
    >
      <div className="input-wrapper">
        <input
          id="location_list"
          type="text"
          name="location"
          list="options"
          placeholder="Search or select a location"
          value={inputValue}
          onChange={handleInputChange}
        />
        {inputValue && (
          <button type="button" className="clear-button" onClick={handleClear}>
            ×
          </button>
        )}
        <datalist id="options">
          {Object.entries(stations).map(([locId, loc]) => (
            <option key={locId} value={loc.name} data-locid={locId}>
              {loc.name}
            </option>
          ))}
        </datalist>
      </div>
      <input id="submit_button" type="submit" value="Submit" />
      {error && <p className="error-message">{error}</p>}
    </form>
  );
};
