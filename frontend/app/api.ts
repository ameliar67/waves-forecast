export interface BuoyStation {
  latitude: number;
  longitude: number;
  name: string;
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
}

const baseUrl = process.env.API_BASE_URL;

export async function getLocations() {
  const response = await fetch(`${baseUrl}/locations`);
  if (!response.ok) {
    throw new Error("Failed to fetch station data");
  }

  const data = await response.json();
  return data?.locations || {};
}

export async function getForecast(id: string): Promise<ForecastData> {
  const response = await fetch(`${baseUrl}/forecast/${id}`);
  if (!response.ok) {
    // TODO
  }

  const data = await response.json();
  return data;
}
