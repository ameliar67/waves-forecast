import React, { useCallback, useMemo, useState } from "react";
import ForecastItem from "./ForecastItem";
import { HourlyForecast } from "./api";

interface WaveChartProps {
  hourlyForecast: HourlyForecast[];
}

const HourlyForecastGrid: React.FC<WaveChartProps> = ({
  hourlyForecast = [],
}) => {
  return (
    <div className="forecast-container">

      <div className="forecast-items">
        {hourlyForecast.length > 0 ? (
          [...hourlyForecast, ...hourlyForecast].map((data, index) => {
            const formattedDate = formatDate(data.date);
            const formattedTime = formatTime(data.date);
            const forecastHeight = data.wave_height.toFixed(1);

            return (
              <ForecastItem
                key={index}
                forecastHeight={forecastHeight}
                formattedTime={formattedTime}
                formattedDate={formattedDate}
              />
            );
          })
        ) : (
          <div>No forecast data available</div>
        )}
      </div>

    </div>
  );
};

function formatDate(date: string) {
  const parsedDate = new Date(date);
  return parsedDate.toLocaleDateString();
}

function formatTime(date: string) {
  const parsedDate = new Date(date);
  return parsedDate.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default HourlyForecastGrid;
