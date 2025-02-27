import React from "react";
import { LocationForm } from "./LocationForm";
import { BuoyStation } from "./api";

interface NoForecastProps {
  errorMessage: React.ReactNode;
  stations: Record<string, BuoyStation>;
  locationId: string;
  locationName: string;
  errorDetails: string;
}

export const ForecastUnavailable: React.FC<NoForecastProps> = ({
  locationName,
  stations,
  locationId,
  errorMessage,
  errorDetails
}) => {
  return (
    <div id="main-container">
      <div className="forecast_header">
        <a href="/" className="wave_and_weather_title">
          Surf Forecast
        </a>
        <p className="title_form_text">{locationName}</p>
        <LocationForm activeStationId={locationId} stations={stations} />
      </div>

      <div className="error-container">
        <p>{errorMessage}</p>
        <p className="error-details">{errorDetails}</p>
      </div>
    </div>
  );
};
