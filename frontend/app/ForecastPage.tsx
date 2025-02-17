import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router";
import {
  BuoyStation,
  ForecastData as ForecastDataModel,
  getForecast,
} from "./api";
import { ForecastData } from "./ForecastData";
import { ForecastLoading } from "./ForecastLoading";
import { Custom500Page } from "./error";

export const ForecastPage: React.FC<{
  stations: Record<string, BuoyStation>;
}> = ({ stations }) => {
  const { locationId } = useParams();
  const [forecastData, setForecastData] = useState<ForecastDataModel | null>(
    null
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
        return (
          <Custom500Page
            errorMessage="Error"
            errorDetails="Errors"
            stations={stations}
            statusCode={500}
            locationId={locationId}
            locationName={locationName || "Unknown"}
          />
        );
      })
      .finally(() => setLoading(false));
  }, [locationId, stations, navigate]);

  if (!loading && !forecastData) {
    return (
      <Custom500Page
      errorMessage="Error"
      errorDetails="Errors"
      stations={stations}
      statusCode={500}
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
