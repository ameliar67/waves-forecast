import React, { useEffect, useState } from "react";
import { useParams } from "react-router";
import { BuoyStation } from "./LocationData";
import { LocationForm } from "./LocationForm";

interface ForecastData {
  wave_height_graph: string;
  current_wave_height: string;
  units: string;
  wind_speed: string;
  wind_direction: string;
  short_forecast: string;
  weather_alerts: string;
  air_temperature: string;
}

export const ForecastPage: React.FC<{ stations: Record<string, BuoyStation> }> = ({ stations }) => {
  const { locationId } = useParams();
  const [forecastData, setForecastData] = useState<ForecastData | null>(null);

  useEffect(() => {
    setForecastData(null);

    (async function () {
      const response = await fetch(`/api/forecast/${locationId}`);
      const data = await response.json();
      setForecastData(data);
    })();
  }, [locationId]);

  // check for forecast

  return (
    <div id="main-container">
      <div className="forecast_header">
        <a href="/" className="wave_and_weather_title">
          Surf Forecast
        </a>
        <p className="title_form_text">{locationId}</p>

        <LocationForm stations={stations} />
      </div>

      <div className="individual_data_fields">
        <div className="wave_data_fields">
          <div className="wave_height_layout">
            <p className="wave_height">
              {forecastData ? `${forecastData.current_wave_height} ${forecastData.units}` : "Loading..."}
            </p>
            <p className="current_wave_height_text" id="current_wave_height">
              Current Wave Height
            </p>
          </div>
        </div>

        <div className="wind_data_fields">
          <div className="alerts_layout">
            <p className="alerts">{forecastData ? forecastData.wind_speed : "Loading..."}</p>
            <p className="current_weather_warnings_text">Current Wind Speed</p>
          </div>
          <div className="alerts_layout">
            <p className="alerts">{forecastData ? forecastData.wind_direction : "Loading..."}</p>
            <p className="current_weather_warnings_text">Current Wind Direction</p>
          </div>
        </div>

        <div className="general_weather_data_fields">
          <div className="alerts_layout">
            <p className="alerts">{forecastData ? forecastData.short_forecast : "Loading..."}</p>
            <p className="current_weather_warnings_text">Current Forecast</p>
          </div>
          <div className="alerts_layout">
            <p className="alerts">{forecastData ? forecastData.weather_alerts : "Loading..."}</p>
            <p className="current_weather_warnings_text">Current Weather Warnings</p>
          </div>
          <div className="alerts_layout">
            <p className="alerts">{forecastData ? forecastData.air_temperature : "Loading..."}</p>
            <p className="current_weather_warnings_text">Current Air Temperature</p>
          </div>
        </div>
      </div>

      <div>
        {forecastData ? (
          <img src={`data:image/png;base64,${forecastData.wave_height_graph}`} alt="Wave Height Graph" />
        ) : (
          "Loading..."
        )}
      </div>
    </div>
  );
};


// (condition ? ifTrue : ifFalse)