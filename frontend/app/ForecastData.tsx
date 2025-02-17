import React from "react";
import { BuoyStation, ForecastData as ForecastDataModel } from "./api";
import { LocationForm } from "./LocationForm";

export interface ForecastDataProps extends ForecastDataModel {
  stations: Record<string, BuoyStation>;
  locationId: string;
  locationName: string;
}

export const ForecastData: React.FC<ForecastDataProps> = ({
  locationId,
  locationName,
  stations,
  ...forecastData
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

      <div className="individual_data_fields">
        <div className="wave_wind_air">
          <div className="wave_data_fields">
            <div className="wave_height_layout">
              <p className="wave_height">
                {forecastData.current_wave_height} ft
              </p>
              <p className="current_wave_height_text" id="current_wave_height">
                Wave Height
              </p>
            </div>
          </div>

          <div className="wind_data_fields">
            <div className="wind_layout">
              <p className="data">{forecastData.wind_speed} knots</p>
              <p className="label">Wind Speed</p>
            </div>
            <div className="wind_layout">
              <p className="data">{forecastData.wind_direction}</p>
              <p className="label">Wind Direction</p>
            </div>
          </div>

          <div className="general_weather_data_fields">
            <div className="forecast_layout">
              <p className="data">{forecastData.short_forecast}</p>
              <p className="label">Forecast</p>
            </div>
            <div className="forecast_layout">
              <p className="data">{forecastData.air_temperature} °F</p>
              <p className="label">Air Temperature</p>
            </div>
          </div>
        </div>

        <div className="alerts_layout">
          <p className="data">{forecastData.weather_alerts}</p>
          <p className="label">Current Weather Warnings</p>
        </div>
      </div>

      <p className="wave_height_graph_label">Wave Height</p>
      <div className="wave_height_graph">
        <img
          src={`data:image/png;base64,${forecastData.wave_height_graph}`}
          alt="Wave Height Graph"
        />
      </div>
    </div>
  );
};
