export interface BuoyStation {
  id: string;
  buoy_latitude: number;
  buoy_longitude: number;
  name: string;
  country: string;
  state: string;
}

export interface TidalForecast {
  date: string;
  tidal_event: string;
}

export interface HourlyForecast {
  max_breaking_height: number;
  min_breaking_height: number;
  wave_height: number;
  date: string;
  time: string;
  air_temperature: number;
  short_forecast: string;
  wind_speed: number;
  wind_direction: number;
  date_time_stamp: string;
  surf_rating: string;
  swell_period: number
}

export interface ForecastData {
  current_wave_height: string;
  wind_speed: number | string;
  wind_direction: number | string;
  short_forecast: string;
  weather_alerts: string;
  air_temperature: number;
  hourly_forecast: HourlyForecast[];
  generated_at: string;
  tide_forecast: TidalForecast[];
  surf_rating: string;
  swell_period: number;
}

// Base url for blob storage direct access endpoints
const storageBaseUrl = process.env.STORAGE_BASE_URL;

function formatDate(date: string) {
  const parsedDate = new Date(date);
  return parsedDate.toLocaleDateString(undefined, {
    weekday: "long",
    month: "short",
    day: "numeric",
  });
}

function formatTime(date: string) {
  const parsedDate = new Date(date);
  return parsedDate.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

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
  if (data?.hourly_forecast?.[0]?.min_breaking_height == null) {
    return { error: "No forecast data available for this location" };
  }

  data["air_temperature"] = data.hourly_forecast[0].air_temperature;
  data["short_forecast"] = data.hourly_forecast[0].short_forecast;
  data["wind_speed"] = data.hourly_forecast[0].wind_speed;
  data["wind_direction"] = data.hourly_forecast[0].wind_direction;
  data["surf_rating"] = data.hourly_forecast[0].surf_rating;
  data["swell_period"] = data.hourly_forecast[0].swell_period;

  //remove past hourly forecasts
  const now = new Date();
  data.hourly_forecast = data.hourly_forecast.filter((forecast) => {
    const forecastDate = new Date(forecast.date);
    return forecastDate >= now;
  });

  for (let entry of data.hourly_forecast) {
    entry.date_time_stamp = entry.date;
    entry.time = formatTime(entry.date_time_stamp);
    entry.date = formatDate(entry.date_time_stamp);
  }

  const generatedAtString =
    formatDate(data.generated_at) + " " + formatTime(data.generated_at);
  data.generated_at = generatedAtString;

  return data;
}
