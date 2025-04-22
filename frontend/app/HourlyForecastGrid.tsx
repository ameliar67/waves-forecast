import React, { useState } from "react";
import ForecastItem from "./ForecastItem";
import { useIsMobile } from "./mobile";
import { formatUnit, useUnits } from "./Units";

interface WaveChartProps {
  hourlyForecast: HourlyForecast[];
}

const HourlyForecastGrid: React.FC<WaveChartProps> = ({
  hourlyForecast = [],
}) => {
  const groupedByDate = groupForecastByDate(hourlyForecast);
  const dateKeys = Object.keys(groupedByDate);
  const [currentIndex, setCurrentIndex] = useState(0);
  const isMobile = useIsMobile();

  if (!hourlyForecast || hourlyForecast.length === 0) {
    return null;
  }

  const units = useUnits();
    setCurrentIndex((prev) => Math.max(prev - 1, 0));
  };

  const handleNext = () => {
    setCurrentIndex((prev) => Math.min(prev + 1, dateKeys.length - 1));
  };

  return (
    <div className="forecast-container">
      {isMobile && (
        <div className="mobile-forecast-nav">
          <button
            type="button"
            onClick={handlePrev}
            className="mobile-forecast-arrow"
            disabled={currentIndex === 0}
          >
            ⬅️
          </button>
          <div className="mobile-forecast-date-label">
            {dateKeys[currentIndex]}
          </div>
          <button
            type="button"
            onClick={handleNext}
            className="mobile-forecast-arrow"
            disabled={currentIndex === dateKeys.length - 1}
          >
            ➡️
          </button>
        </div>
      )}

      {dateKeys.map((date, index) => {
        if (isMobile && index !== currentIndex) return null;

        return (
          <div key={date} className="forecast-day-group">
            {!isMobile && <div className="forecast-date-banner">{date}</div>}
            <div className="forecast-items">
              {groupedByDate[date].map((data, i) => (
                <ForecastItem
                  key={i}
                  forecastHeight={formatUnit(
                    (data.max_breaking_height + data.min_breaking_height) / 2,
                    units.distance,
                    1
                  )}
                  formattedTime={formatTime(data.date)}
                />
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
};

function groupForecastByDate(forecast: HourlyForecast[]) {
  return forecast.reduce<Record<string, HourlyForecast[]>>((acc, item) => {
    const dateKey = formatDate(item.date);
    if (!acc[dateKey]) acc[dateKey] = [];
    acc[dateKey].push(item);
    return acc;
  }, {});
}

function formatDate(date: string) {
  const parsedDate = new Date(date);
  return parsedDate.toLocaleDateString(undefined, {
    weekday: "long",
    month: "short",
    day: "numeric",
  });
}

function formatTime(date: string) {
  const parsedDate = new Date(date);
  return parsedDate.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default HourlyForecastGrid;
