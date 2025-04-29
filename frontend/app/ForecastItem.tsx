import React from "react";
import { formatUnit, useUnits } from "./Units";

interface ForecastItemProps {
  forecastHeight: string;
  formattedTime: string;
  airTemperature: number;
  windSpeed: number;
  windDirection: number;
}

const ForecastItem: React.FC<ForecastItemProps> = ({
  forecastHeight,
  formattedTime,
  airTemperature,
  windSpeed,
  windDirection,
}) => {
  const units = useUnits();

  const direction =
    typeof windDirection !== "number"
      ? ""
      : ["N", "E", "S", "W"][Math.floor((windDirection + 45) / 90) % 4];

  return (
    <div className="forecast-item">
      <div className="forecast-time">{formattedTime}</div>
      <div className="forecast-height">
        {!forecastHeight ? "-" : forecastHeight}
      </div>
      <div className="forecast-air-temperature">
        Air Temperature:{" "}
        {!airTemperature ? "-" : formatUnit(airTemperature, units.temperature)}
      </div>
      <div className="wind-speed">
        Wind Speed: {!windSpeed ? "-" : windSpeed + " knots"}
      </div>
      <div className="wind-direction">
        Wind Direction: {!windDirection ? "-" : direction + " " + windDirection}
      </div>
    </div>
  );
};

export default ForecastItem;
