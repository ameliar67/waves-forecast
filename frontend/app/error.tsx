import React from "react";
import { LocationForm } from "./LocationForm";
import { BuoyStation } from "./api";

interface ErrorPageProps {
  errorMessage: string;
  statusCode: number;
  errorDetails?: string;
  stations: Record<string, BuoyStation>;
  locationId: string,
  locationName: string,
}

export const Custom500Page: React.FC<ErrorPageProps> = ({
  statusCode,
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

      <div style={{ textAlign: "center", padding: "50px" }}>
        <h1>{statusCode} Page Not Found</h1>
        <p>{errorMessage}</p>
        <pre>{errorDetails}</pre>
      </div>
    </div>
  );
};
