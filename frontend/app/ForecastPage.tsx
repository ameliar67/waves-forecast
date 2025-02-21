import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router";
import {
  BuoyStation,
  ForecastData as ForecastDataModel,
  getForecast,
} from "./api";
import { ForecastData } from "./ForecastData";
import { ForecastLoading } from "./ForecastLoading";
import { ForecastUnavailable } from "./NotFound";

export const ForecastPage: React.FC<{
  stations: Record<string, BuoyStation>;
}> = ({ stations }) => {
  const { locationId } = useParams();
  const [forecastData, setForecastData] = useState<ForecastDataModel | null>(
    null,
  );
  const [locationName, setLocationName] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (!locationId) return;

    setLocationName(stations[locationId]?.name || "Unknown Station");
    setLoading(true);
    setForecastData(null);

    // Fetch forecast data and location name when locationId changes
    getForecast(locationId)
      .then((f) => setForecastData(f))
      .catch((err) => {
        console.error("Error fetching data:", err);
      })
      .finally(() => setLoading(false));
  }, [locationId, stations, navigate]);

  if (!loading && !forecastData) {
    return (
      <ForecastUnavailable
        errorMessage="No forecast data currently available for selected location"
        stations={stations}
        errorDetails="Please select another location"
        locationId={locationId || "Unknown"}
        locationName={locationName || "Unknown"}
      />
    );
  }

  return (
    <div>
      {/* My common components */}
      {stations && forecastData ? (
        <ForecastData
          locationId={locationId!}
          locationName={locationName!}
          stations={stations}
          {...forecastData}
        />
      ) : (
        <ForecastLoading
          locationId={locationId!}
          locationName={locationName!}
          stations={stations}
        />
      )}
    </div>
  );
};
