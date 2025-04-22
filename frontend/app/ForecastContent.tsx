import React from "react";
import { ForecastData } from "./api";
import HourlyForecastGrid from "./HourlyForecastGrid";
import { LocationForm } from "./LocationForm";
import { useStations } from "./Stations";
import { formatUnit, useUnits } from "./Units";
import WaveChart from "./WaveChart";

export interface ForecastContentProps {
  forecastData: ForecastData;
  locationId: string;
}

export const ForecastContent: React.FC<ForecastContentProps> = ({
  locationId,
  forecastData,
}) => {
  const { max_breaking_height = 0, min_breaking_height = 0 } =
    forecastData?.hourly_forecast?.[0] ?? {};

  const units = useUnits();

  const averageBreakingHeight = units.distance.convert(
    (max_breaking_height + min_breaking_height) / 2
  );
  const roundedLower = Math.floor(averageBreakingHeight);
  const roundedUpper = Math.ceil(averageBreakingHeight);

  const stations = useStations();

  const direction =
    typeof forecastData.wind_direction !== "number"
      ? ""
      : ["N", "E", "S", "W"][
          Math.floor((forecastData.wind_direction + 45) / 90) % 4
        ];

  return (
    <>
      <div className="forecast-header">
        <a href="/" className="wave-and-weather-title">
          Surf Forecast
        </a>
        <LocationForm activeStationId={locationId} />
      </div>

      <p className="location-name">{stations[locationId]["name"]}</p>
      <p className="location-details">
        {stations[locationId]["state"]}, {stations[locationId]["country"]}
      </p>

      <div className="individual-data-fields">
        <div className="wave-wind-air">
          <div className="wave-data-fields">
            <div className="wave-height-layout">
              <p className="wave-height">
                {roundedLower === 0 && roundedUpper === 0
                  ? "Flat"
                  : formatUnit(roundedLower - roundedUpper, units.distance)}
              </p>
              <p className="label">Wave Height</p>
            </div>
          </div>

          <div className="wind-data-fields">
            <div className="wind-layout">
              <p className="data">
                {forecastData.wind_speed == "No forecast available"
                  ? forecastData.wind_speed
                  : forecastData.wind_speed + " knots"}
              </p>
              <p className="label">Wind Speed</p>
            </div>
            <div className="wind-layout">
              <div className="wind-direction-layout">
                <p className="data">
                  {direction} {forecastData.wind_direction}
                </p>
                {forecastData.wind_direction !== "No forecast available" && (
                  <div
                    className="wind-arrow"
                    style={{
                      transform: `rotate(${forecastData.wind_direction}deg)`,
                    }}
                  ></div>
                )}
              </div>
              <p className="label">Wind Direction</p>
            </div>
          </div>

          <div className="general-weather-data-fields">
            <div className="forecast-layout">
              <p className="data">{forecastData.short_forecast}</p>
              <p className="label">Forecast</p>
            </div>
            <div className="forecast-layout">
              <p className="data">
                {typeof forecastData.air_temperature === "string"
                  ? forecastData.air_temperature
                  : formatUnit(forecastData.air_temperature, units.temperature)}
              </p>
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
      <p id="number-of-days-label">16 Day Forecast</p>
      <p id="generation-time">
        Last generated at{" "}
        {new Date(forecastData.generated_at).toLocaleString("en-US", {
          weekday: "long",
          year: "numeric",
          month: "long",
          day: "numeric",
          hour: "numeric",
          minute: "2-digit",
          hour12: true,
        })}
      </p>
      <HourlyForecastGrid hourlyForecast={forecastData.hourly_forecast} />
      <WaveChart hourlyForecast={forecastData.hourly_forecast} />
    </>
  );
};
