import React, { useCallback, useMemo, useState } from "react";
import { HourlyForecast } from "./api";
import ForecastItem from "./ForecastItem";
import { useIsMobile } from "./mobile";
import { useUnits } from "./Units";

interface WaveChartProps {
  hourlyForecast: HourlyForecast[];
}

const HourlyForecastGrid: React.FC<WaveChartProps> = ({
  hourlyForecast = [],
}) => {
  const groupedByDate = useMemo(
    () => groupForecastByDate(hourlyForecast),
    [hourlyForecast]
  );
  const dateKeys = Object.keys(groupedByDate);
  const [currentIndex, setCurrentIndex] = useState(0);
  const isMobile = useIsMobile();

  if (!hourlyForecast || hourlyForecast.length === 0) {
    return null;
  }

  const units = useUnits();
  const handlePrev = useCallback(() => {
    setCurrentIndex((prev) => Math.max(prev - 1, 0));
  }, []);

  const handleNext = useCallback(() => {
    setCurrentIndex((prev) => Math.min(prev + 1, dateKeys.length - 1));
  }, [dateKeys.length]);

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
              {groupedByDate[date].map((data, i) => {
                const averageBreakingHeight = units.distance.convert(
                  (data.max_breaking_height + data.min_breaking_height) / 2
                );
                return (
                  <ForecastItem
                    key={i}
                    forecastHeight={
                      averageBreakingHeight < 1
                        ? "Flat"
                        : `${Math.floor(averageBreakingHeight)} - ${Math.ceil(averageBreakingHeight)} ft`
                    }
                    formattedTime={data.time}
                    airTemperature={data.air_temperature}
                    windSpeed={data.wind_speed}
                    windDirection={data.wind_direction}
                  />
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
};

function groupForecastByDate(forecast: HourlyForecast[]) {
  return forecast.reduce<Record<string, HourlyForecast[]>>((acc, item) => {
    const dateKey = item.date;
    if (!acc[dateKey]) acc[dateKey] = [];
    acc[dateKey].push(item);
    return acc;
  }, {});
}

export default HourlyForecastGrid;
