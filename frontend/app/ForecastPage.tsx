import React, { useEffect, useState } from "react";
import { useParams } from "react-router";
import {
  BuoyStation,
  ForecastData as ForecastDataModel,
  getForecast,
} from "./api";
import { ForecastContent } from "./ForecastContent";
import { ForecastLoading } from "./ForecastLoading";
import { ForecastUnavailable } from "./NotFound";

export const ForecastPage: React.FC<{
  stations: Record<string, BuoyStation>;
}> = ({ stations }) => {
  const { locationId } = useParams();
  const [forecastData, setForecastData] = useState<ForecastDataModel | null>(
    null
  );
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    if (!locationId) return;

    setLoading(true);
    setForecastData(null);

    // Fetch forecast data and location name when locationId changes
    getForecast(locationId)
      .then((f) => setForecastData(f))
      .catch((err) => {
        console.error("Error fetching data:", err);
      })
      .finally(() => setLoading(false));
  }, [locationId]);

  if (!loading && !forecastData) {
    return (
      <ForecastUnavailable
        errorMessage="No forecast data currently available for selected location"
        stations={stations}
        errorDetails="Please select another location"
        locationId={locationId || "Unknown"}
      />
    );
  }

  return stations && forecastData ? (
    <ForecastContent
      locationId={locationId!}
      stations={stations}
      forecastData={forecastData}
    />
  ) : (
    <ForecastLoading locationId={locationId!} stations={stations} />
  );
};
