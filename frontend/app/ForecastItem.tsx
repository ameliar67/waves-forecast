import React from "react";
import { formatUnit, useUnits } from "./Units";

interface ForecastItemProps {
  forecastHeight: string;
  formattedTime: string;
  airTemperature: number;
  windSpeed: number;
  windDirection: number;
  surfRating: string;
}

const ForecastItem: React.FC<ForecastItemProps> = ({
  forecastHeight,
  formattedTime,
  airTemperature,
  windSpeed,
  windDirection,
  surfRating,
}) => {
  const units = useUnits();
  type SurfRating = "Epic" | "Good" | "Fair" | "Poor";

  const ratingColors: Record<SurfRating, string> = {
    Epic: "purple",
    Good: "green",
    Fair: "orange",
    Poor: "red",
  };

  let ratingColor =
    ratingColors[surfRating as SurfRating] || "black";

  const direction =
    typeof windDirection !== "number"
      ? ""
      : ["N", "E", "S", "W"][Math.floor((windDirection + 45) / 90) % 4];

  return (
    <div
      className="forecast-item"
      style={{
        backgroundImage: `linear-gradient(to top, ${ratingColor}, ${ratingColor} 5%, transparent 2%, transparent 5%)`,
      }}
    >
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
      <div className="wind-direction">
        Surf Rating: {!surfRating ? "-" : surfRating}
      </div>
    </div>
  );
};

export default ForecastItem;
