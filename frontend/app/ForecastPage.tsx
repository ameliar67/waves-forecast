import React, { useEffect, useState } from "react";
import { useParams } from "react-router";
import { ForecastData as ForecastDataModel, getForecast } from "./api";
import { ForecastContent } from "./ForecastContent";
import { ForecastLoading } from "./ForecastLoading";
import { ForecastUnavailable } from "./NotFound";

export const ForecastPage: React.FC = () => {
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
        errorDetails="Please select another location"
        locationId={locationId || "Unknown"}
      />
    );
  }

  return forecastData ? (
    <ForecastContent locationId={locationId!} forecastData={forecastData} />
  ) : (
    <ForecastLoading locationId={locationId!} />
  );
};
