export interface BuoyStation {
  id: string;
  latitude: number;
  longitude: number;
  name: string;
  country: string;
  state: string;
}

export interface ForecastData {
  wave_height_graph: string;
  current_wave_height: string;
  units: string;
  wind_speed: string;
  wind_direction: string;
  short_forecast: string;
  weather_alerts: string;
  air_temperature: string;
  hourly_forecast: [number];
  forecast_hours: [string];
  forecast_dates: [string];
}

//Locations data is kept in blob storage as it doesn't change often
//Forecast data changes often and is regenerated via azure functions unless
//already stored in cache

// Base url for Azure function endpoints
const apiBaseUrl = process.env.API_BASE_URL;

// Base url for blob storage direct access endpoints
const storageBaseUrl = process.env.STORAGE_BASE_URL;

//Retreive location data from blob storage
export async function getLocations() {
  const response = await fetch(`${storageBaseUrl}/locations`);
  if (!response.ok) {
    throw new Error("Failed to fetch station data");
  }

  const data = await response.json();
  return data?.locations || {};
}

//Retrieve forecast data from Azure function API
export async function getForecast(id: string): Promise<ForecastData> {
  const response = await fetch(`${apiBaseUrl}/forecast/${id}`);
  if (!response.ok) {
    throw new Error("Failed to fetch forecast data");
  }

  const data = await response.json();
  return data;
}
