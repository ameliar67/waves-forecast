import React from "react";
import { BuoyStation } from "./api";
import { LocationForm } from "./LocationForm";
import ProgressBar from "./ProgressBar";

export interface ForecastLoadingProps {
  stations: Record<string, BuoyStation>;
  locationId: string;
}

export const ForecastLoading: React.FC<ForecastLoadingProps> = ({
  locationId,
  stations,
}) => {
  return (
    <>
      <div className="forecast-header">
        <a href="/" className="wave-and-weather-title">
          Surf Forecast
        </a>

        <LocationForm activeStationId={locationId} stations={stations} />
      </div>
      <ProgressBar containerHeight={100}></ProgressBar>
      <p className="loading-forecast-text">Loading Forecast...</p>
    </>
  );
};
