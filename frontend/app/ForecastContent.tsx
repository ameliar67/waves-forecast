import React from "react";
import { BuoyStation, ForecastData as ForecastDataModel } from "./api";
import { LocationForm } from "./LocationForm";

export interface ForecastContentProps extends ForecastDataModel {
  stations: Record<string, BuoyStation>;
  locationId: string;
  locationName: string;
}

export const ForecastContent: React.FC<ForecastContentProps> = ({
  locationId,
  locationName,
  stations,
  ...forecastData
}) => {
  return (
    <>
      <div className="forecast-header">
        <a href="/" className="wave-and-weather-title">
          Surf Forecast
        </a>

        <LocationForm activeStationId={locationId} stations={stations} />
      </div>

      <div className="individual-data-fields">
        <div className="wave-wind-air">
          <div className="wave-data-fields">
            <div className="wave-height-layout">
              <p className="wave-height">
                {forecastData.current_wave_height} ft
              </p>
              <p className="label">
                Wave Height
              </p>
            </div>
          </div>

          <div className="wind-data-fields">
            <div className="wind-layout">
              <p className="data">{forecastData.wind_speed} knots</p>
              <p className="label">Wind Speed</p>
            </div>
            <div className="wind-layout">
              <p className="data">{forecastData.wind_direction}</p>
              <p className="label">Wind Direction</p>
            </div>
          </div>

          <div className="general-weather-data-fields">
            <div className="forecast-layout">
              <p className="data">{forecastData.short_forecast}</p>
              <p className="label">Forecast</p>
            </div>
            <div className="forecast-layout">
              <p className="data">{forecastData.air_temperature} °F</p>
              <p className="label">Air Temperature</p>
            </div>
          </div>
        </div>

        <div className="alerts-layout">
          {forecastData.weather_alerts !== "None" ? (
            <>
              <p className="data">{forecastData.weather_alerts}</p>
              <p className="label">Current Weather Warnings</p>
            </>
          ) : (
            <p className="no-alerts">No current weather warnings</p>
          )}
        </div>
      </div>

      <div className="wave-height-graph">
        <img
          src={`data:image/png;base64,${forecastData.wave_height_graph}`}
          alt="Wave Height Graph"
        />
      </div>
    </>
  );
};
