import React from "react";
import { ForecastData as ForecastDataModel } from "./api";

export const HourlyForecastGrid: React.FC<ForecastDataModel> = ({
  ...forecastData
}) => {
  return (
    <div className="forecast-container">
      <div className="forecast-title">Hourly Forecast</div>
      <div className="forecast-items">
        {forecastData.forecast_hours.map((hours, index) => (
          <div className="forecast-item" key={index}>
            <div className="forecast-height">
              {forecastData.hourly_forecast[index].toFixed(1)} ft
            </div>
            <div className="forecast-time">{hours}</div>
            <div className="forecast-date">
              {forecastData.forecast_dates[index]}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
