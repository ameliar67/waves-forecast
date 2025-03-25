import React from "react";
import { LocationForm } from "./LocationForm";

interface NoForecastProps {
  errorMessage: React.ReactNode;
  locationId: string;
  errorDetails: string;
}

export const ForecastUnavailable: React.FC<NoForecastProps> = ({
  locationId,
  errorMessage,
  errorDetails,
}) => {
  return (
    <>
      <div className="forecast-header">
        <a href="/" className="wave-and-weather-title">
          Surf Forecast
        </a>
        <LocationForm activeStationId={locationId} />
      </div>

      <div className="error-container">
        <p className="error-message">{errorMessage}</p>
        <p className="error-details">{errorDetails}</p>
      </div>
    </>
  );
};
