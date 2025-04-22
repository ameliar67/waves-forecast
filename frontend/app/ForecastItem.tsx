import React from "react";

interface ForecastItemProps {
  forecastHeight: string;
  formattedTime: string;
}

const ForecastItem: React.FC<ForecastItemProps> = ({
  forecastHeight,
  formattedTime,
}) => {
  return (
    <div className="forecast-item">
      <div className="forecast-time">{formattedTime}</div>
      <div className="forecast-height">{forecastHeight}</div>
    </div>
  );
};

export default ForecastItem;
