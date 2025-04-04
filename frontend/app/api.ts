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
export async function getForecast(id: string): Promise<ForecastData> {
  const response = await fetch(`${storageBaseUrl}/forecast/${id}`);
  if (!response.ok) {
    throw new Error("Failed to fetch forecast data");
  }

  const data = await response.json();
  return data;
}
