import React from "react";
import { BuoyStation } from "./api";
import { LocationForm } from "./LocationForm";
import ProgressBar from "./ProgressBar"

export interface ForecastLoadingProps {
  stations: Record<string, BuoyStation>;
  locationId: string;
  locationName: string;
}

export const ForecastLoading: React.FC<ForecastLoadingProps> = ({
  locationId,
  locationName,
  stations,
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
      <ProgressBar containerHeight={100}></ProgressBar>
      <p>Loading Forecast...</p>
    </div>
  );
};
