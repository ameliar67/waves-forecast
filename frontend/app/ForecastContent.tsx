import React from "react";
import { ForecastData } from "./api";
import HourlyForecastGrid from "./HourlyForecastGrid";
import { LocationForm } from "./LocationForm";
import WaveChart from "./WaveChart";

export interface ForecastContentProps {
  forecastData: ForecastData;
  locationId: string;
}

export const ForecastContent: React.FC<ForecastContentProps> = ({
  locationId,
  forecastData,
}) => {
  const forecastHeight = Math.round(forecastData.hourly_forecast[0].wave_height);
  return (
    <>
      <div className="forecast-header">
        <a href="/" className="wave-and-weather-title">
          Surf Forecast
        </a>
        <LocationForm activeStationId={locationId} />
      </div>

      <div className="individual-data-fields">
        <div className="wave-wind-air">
          <div className="wave-data-fields">
            <div className="wave-height-layout">
              <p className="wave-height">
                {forecastHeight} ft
              </p>
              <p className="label">Wave Height</p>
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
              <p className="label">Current Weather Warnings:</p>
              <p id="weather-alerts" className="data">
                {forecastData.weather_alerts}
              </p>
            </>
          ) : (
            <p className="no-alerts">No current weather warnings</p>
          )}
        </div>
      </div>
      <HourlyForecastGrid hourlyForecast={forecastData.hourly_forecast} />
      <WaveChart hourlyForecast={forecastData.hourly_forecast} />
    </>
  );
};
