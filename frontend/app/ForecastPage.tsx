import React, { useEffect, useState } from "react";
import { useParams } from "react-router";
import { BuoyStation, ForecastData, getForecast } from "./api";
import { LocationForm } from "./LocationForm";
import ProgressBar from "./ProgressBar";

export const ForecastPage: React.FC<{
  stations: Record<string, BuoyStation>;
}> = ({ stations }) => {
  const { locationId } = useParams();
  const [forecastData, setForecastData] = useState<ForecastData | null>(null);
  const [locationName, setLocationName] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    if (!locationId) return;

    setLocationName(stations[locationId]?.name || "Unknown Station");
    setLoading(true);
    setForecastData(null);

    // Fetch forecast data and location name when locationId changes
    getForecast(locationId)
      .then((f) => setForecastData(f))
      .catch((err) => console.error("Error fetching data:", err))
      .finally(() => setLoading(false));
  }, [locationId, stations]);

  if (!loading && !forecastData) return <div>No data available</div>;

  return (
    <div id="main-container">
      <div className="forecast_header">
        <a href="/" className="wave_and_weather_title">
          Surf Forecast
        </a>
        <p className="title_form_text">{locationName}</p>

        <LocationForm stations={stations} />
      </div>

      <div className="individual_data_fields">
        <div className="wave_wind_air">
          <div className="wave_data_fields">
            <div className="wave_height_layout">
              <p className="wave_height">
                {forecastData ? (
                  `${forecastData.current_wave_height} ft`
                ) : (
                  <ProgressBar containerHeight={100}></ProgressBar>
                )}
              </p>
              <p className="current_wave_height_text" id="current_wave_height">
                Wave Height
              </p>
            </div>
          </div>

          <div className="wind_data_fields">
            <div className="wind_layout">
              <p className="data">
                {forecastData ? forecastData.wind_speed + " knots" : ""}
              </p>
              <p className="label">Wind Speed</p>
            </div>
            <div className="wind_layout">
              <p className="data">
                {forecastData ? forecastData.wind_direction : ""}
              </p>
              <p className="label">Wind Direction</p>
            </div>
          </div>

          <div className="general_weather_data_fields">
            <div className="forecast_layout">
              <p className="data">
                {forecastData ? forecastData.short_forecast : ""}
              </p>
              <p className="label">Forecast</p>
            </div>
            <div className="forecast_layout">
              <p className="data">
                {forecastData
                  ? forecastData.air_temperature + "° Fahrenheit"
                  : ""}
              </p>
              <p className="label">Air Temperature</p>
            </div>
          </div>
        </div>

        <div className="alerts_layout">
          <p className="data">
            {forecastData ? (
              forecastData.weather_alerts
            ) : (
              <ProgressBar containerHeight={20}></ProgressBar>
            )}
          </p>
          <p className="label">Current Weather Warnings</p>
        </div>
      </div>

      <p className="wave_height_graph_label">
        {forecastData ? "Wave Height" : ""}
      </p>
      <div className="wave_height_graph">
        {forecastData ? (
          <img
            src={`data:image/png;base64,${forecastData.wave_height_graph}`}
            alt="Wave Height Graph"
          />
        ) : (
          ""
        )}
      </div>
    </div>
  );
};
