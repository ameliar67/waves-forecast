import React, { useEffect, useState } from "react";
import { useParams } from "react-router";
import { getForecast } from "./api";
import { ForecastContent } from "./ForecastContent";
import { ForecastLoading } from "./ForecastLoading";
import { ForecastUnavailable } from "./NotFound";

export const ForecastPage: React.FC = () => {
  const { locationId } = useParams();
  const [forecastData, setForecastData] = useState<Awaited<
    ReturnType<typeof getForecast>
  > | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    if (!locationId) return;

    setLoading(true);
    setForecastData(null);

    // Fetch forecast data and location name when locationId changes
    getForecast(locationId)
      .then((f) => setForecastData(f))
      .finally(() => setLoading(false));
  }, [locationId]);

  if (loading || forecastData === null) {
    return <ForecastLoading locationId={locationId!} />;
  }

  return "error" in forecastData ? (
    <ForecastUnavailable
      errorMessage="No forecast data currently available for selected location"
      errorDetails="Please select another location"
      locationId={locationId || "Unknown"}
    />
  ) : (
    <ForecastContent locationId={locationId!} forecastData={forecastData} />
  );
};
