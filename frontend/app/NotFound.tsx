import React from "react";
import { LocationForm } from "./LocationForm";

interface NoForecastProps {
  errorMessage: React.ReactNode;
  locationId: string;
  errorDetails: string;
}

const logo = new URL("./surf-logo.svg", import.meta.url) as unknown as string;

export const ForecastUnavailable: React.FC<NoForecastProps> = ({
  locationId,
  errorMessage,
  errorDetails,
}) => {
  return (
    <>
      <div className="forecast-header">
        <a href="/" className="wave-and-weather-title">
          <img id="surf-logo-forecast-page" src={logo} alt="Surf Logo" />
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
