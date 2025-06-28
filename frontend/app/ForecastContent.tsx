import React from "react";
import { ForecastData } from "./api";
import HourlyForecastGrid from "./HourlyForecastGrid";
import { LocationForm } from "./LocationForm";
import { useStations } from "./Stations";
import { formatUnit, useUnits } from "./Units";
import WaveChart from "./WaveChart";
import TideGraph from "./TideGraph";

const logo = new URL("./surf-logo.svg", import.meta.url) as unknown as string;

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
  // Upper and lower bound of wave height range
  // Display a typical wave height range to give better idea of expected surf conditions
  const lowerRange = Math.floor(averageBreakingHeight);
  const upperRange = Math.ceil(averageBreakingHeight);

  const stations = useStations();
  type SurfRating = "Epic" | "Good" | "Fair" | "Poor";

  const ratingColors: Record<SurfRating, string> = {
    Epic: "purple",
    Good: "green",
    Fair: "orange",
    Poor: "red",
  };

  let ratingColor =
    ratingColors[forecastData.surf_rating as SurfRating] || "black";

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
          <img id="surf-logo-forecast-page" src={logo} alt="Surf Logo" />
          Surf Sage
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
              <p className="label">
                {forecastData.hourly_forecast[0]
                  ? forecastData.hourly_forecast[0].date +
                    " " +
                    forecastData.hourly_forecast[0].time
                  : ""}
              </p>
              <p className="wave-height" style={{ color: `${ratingColor}` }}>
                {lowerRange === 0 && upperRange === 0
                  ? "Flat"
                  : `${lowerRange}-${upperRange} ft`}
              </p>
              <p className="label">Wave Height</p>
              <p id="swell_period">
                {forecastData.hourly_forecast[0]?.swell_period &&
                  forecastData.hourly_forecast[0].swell_period + " seconds"}
              </p>
              <p className="label">
                {forecastData.hourly_forecast[0]?.swell_period &&
                  "Swell Period"}
              </p>
            </div>
          </div>

          <div className="wind-data-fields">
            <div className="wind-layout">
              <p className="data">
                {!forecastData.wind_speed
                  ? "No wind speed available"
                  : forecastData.wind_speed + " knots"}
              </p>
              <p className="label">Wind Speed</p>
            </div>
            <div className="wind-layout">
              <div className="wind-direction-layout">
                <p className="data">
                  {!forecastData.wind_direction
                    ? "No wind direction available"
                    : direction + " " + forecastData.wind_direction}
                </p>
                {forecastData.wind_direction && (
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
              <p className="data">
                {" "}
                {!forecastData.short_forecast
                  ? "No forecast available"
                  : forecastData.short_forecast}
              </p>
              <p className="label">Weather Forecast</p>
            </div>
            <div className="forecast-layout">
              <p className="data">
                {!forecastData.air_temperature
                  ? "No air temperature available"
                  : formatUnit(forecastData.air_temperature, units.temperature)}
              </p>
              <p className="label">Air Temperature</p>
            </div>
          </div>
        </div>

        <div
          className="alerts-layout"
          style={{ "--shadow-color": `${ratingColor}` } as React.CSSProperties}
        >
          {forecastData.surf_rating ? (
            <>
              <p className="surf-rating" style={{ color: `${ratingColor}` }}>
                Surf Rating: {forecastData.surf_rating}
              </p>
            </>
          ) : (
            <p className="surf-rating">No surf rating available</p>
          )}
          {forecastData.weather_alerts !== "None" ? (
            <>
              <p className="weather-warning-label">Current Weather Warnings:</p>
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
      <p id="generation-time">Last generated at {forecastData.generated_at}</p>
      <HourlyForecastGrid hourlyForecast={forecastData.hourly_forecast} />
      <TideGraph tidalForecast={forecastData.tide_forecast} />
      <p id="wave-height-graph-title">
        {!forecastData.hourly_forecast[0] ? "" : "Wave and Swell Height"}
      </p>
      <WaveChart hourlyForecast={forecastData.hourly_forecast} />
    </>
  );
};
