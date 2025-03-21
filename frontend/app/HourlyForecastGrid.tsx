import React from "react";

interface HourlyForecast {
  max_breaking_height: number;
  min_breaking_height: number;
  wave_height: number;
  date: string; // ISO 8601 date format
}

interface ForecastData {
  hourly_forecast: HourlyForecast[];
}

interface WaveChartProps {
  forecastData: ForecastData;
}

const HourlyForecastGrid: React.FC<WaveChartProps> = ({ forecastData }) => {
  const { hourly_forecast = [] } = forecastData;

  return (
    <div className="forecast-container">
      <div className="forecast-title">Hourly Forecast</div>
      <div className="forecast-items">
        {hourly_forecast.length > 0 ? (
          hourly_forecast.map((data, index) => {
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
