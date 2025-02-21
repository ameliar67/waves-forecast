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
      <div className="forecast_header">
        <a href="/" className="wave_and_weather_title">
          Surf Forecast
        </a>

        <LocationForm activeStationId={locationId} stations={stations} />
      </div>
      <ProgressBar containerHeight={100}></ProgressBar>
      <p>Loading Forecast...</p>
    </>
  );
};
