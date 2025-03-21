import React from "react";
import { HourlyForecast } from "./api";

interface WaveChartProps {
  hourlyForecast: HourlyForecast[];
}

const HourlyForecastGrid: React.FC<WaveChartProps> = ({
  hourlyForecast = [],
}) => {
  return (
    <div className="forecast-container">
      <div className="forecast-title">Hourly Forecast</div>
      <div className="forecast-items">
        {hourlyForecast.length > 0 ? (
          hourlyForecast.map((data, index) => {
            // Use the built-in Date constructor to parse the ISO 8601 date string
            const date = new Date(data.date);

            // Format the date (MM/DD/YYYY)
            const formattedDate = date.toLocaleDateString();
            // Format the time (HH:MM) without seconds
            const formattedTime = date.toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            });

            const forecastHeight = data.wave_height.toFixed(1);

            return (
              <div key={index} className="forecast-item">
                <div className="forecast-height">{forecastHeight} ft</div>
                <div className="forecast-time">{formattedTime}</div>
                <div className="forecast-date">{formattedDate}</div>
              </div>
            );
          })
        ) : (
          <div>No forecast data available</div>
        )}
      </div>
    </div>
  );
};

export default HourlyForecastGrid;
