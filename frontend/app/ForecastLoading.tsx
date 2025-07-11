import React from "react";
import { LocationForm } from "./LocationForm";
import ProgressBar from "./ProgressBar";

export interface ForecastLoadingProps {
  locationId: string;
}

export const ForecastLoading: React.FC<ForecastLoadingProps> = ({
  locationId,
}) => {
  return (
    <>
      <div className="forecast-header">
        <a href="/" className="wave-and-weather-title">
          Surf Sage
        </a>

        <LocationForm activeStationId={locationId} />
      </div>
      <ProgressBar containerHeight={100}></ProgressBar>
      <p className="loading-forecast-text">Loading Forecast...</p>
    </>
  );
};
