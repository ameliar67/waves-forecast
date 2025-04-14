export interface BuoyStation {
  id: string;
  latitude: number;
  longitude: number;
  name: string;
  country: string;
  state: string;
}

export interface HourlyForecast {
  max_breaking_height: number;
  min_breaking_height: number;
  wave_height: number;
  date: string;
}

export interface ForecastData {
  current_wave_height: string;
  wind_speed: string;
  wind_direction: string;
  short_forecast: string;
  weather_alerts: string;
  air_temperature: string;
  hourly_forecast: HourlyForecast[];
}

// Base url for blob storage direct access endpoints
const storageBaseUrl = process.env.STORAGE_BASE_URL;

// Retrieve location data from blob storage
export async function getLocations() {
  const response = await fetch(`${storageBaseUrl}/locations`);
  if (!response.ok) {
    throw new Error("Failed to fetch station data");
  }

  const data = await response.json();
  return data?.locations || {};
}

// Retrieve forecast data from blob storage
export async function getForecast(
  id: string
): Promise<ForecastData | { error: string }> {
  const response = await fetch(`${storageBaseUrl}/forecast/${id}`);
  if (!response.ok) {
    return { error: "Failed to fetch forecast data" };
  }

  const data: ForecastData = await response.json();
  if (data?.hourly_forecast?.[0]?.min_breaking_height == null || data?.air_temperature === "No forecast available") {
    return { error: "No forecast data available for this location" };
  }

  const now = new Date();
  data.hourly_forecast = data.hourly_forecast.filter((forecast) => {
    const forecastDate = new Date(forecast.date);
    return forecastDate >= now;
  });
  return data;
}
