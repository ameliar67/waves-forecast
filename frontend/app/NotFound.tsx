import React from "react";
import { LocationForm } from "./LocationForm";
import { BuoyStation } from "./api";

interface NoForecastProps {
  errorMessage: React.ReactNode;
  stations: Record<string, BuoyStation>;
  locationId: string;
  errorDetails: string;
}

export const ForecastUnavailable: React.FC<NoForecastProps> = ({
  stations,
  locationId,
  errorMessage,
  errorDetails,
}) => {
  return (
    <>
      <div className="forecast_header">
        <a href="/" className="wave_and_weather_title">
          Surf Forecast
        </a>
        <LocationForm activeStationId={locationId} stations={stations} />
      </div>

      <div className="error-container">
        <p className="error-message">{errorMessage}</p>
        <p className="error-details">{errorDetails}</p>
      </div>
    </>
  );
};
