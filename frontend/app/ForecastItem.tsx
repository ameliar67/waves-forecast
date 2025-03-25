import React from "react";

interface ForecastItemProps {
  forecastHeight: string;
  formattedTime: string;
  formattedDate: string;
}

const ForecastItem: React.FC<ForecastItemProps> = ({
  forecastHeight,
  formattedTime,
  formattedDate,
}) => (
  <div className="forecast-item">
    <div className="forecast-height">{forecastHeight} ft</div>
    <div className="forecast-time">{formattedTime}</div>
    <div className="forecast-date">{formattedDate}</div>
  </div>
);

export default ForecastItem;
