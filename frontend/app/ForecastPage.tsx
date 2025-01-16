import React, { useEffect, useState } from "react";
import { useParams } from "react-router";
import { BuoyStation } from "./LocationData";
import { LocationForm } from "./LocationForm";

interface ForecastData {
  wave_height_graph: string;
  current_wave_height: string;
  units: string;
  wind_speed: string;
  wind_direction: string;
  short_forecast: string;
  weather_alerts: string;
  air_temperature: string;
}

export const ForecastPage: React.FC<{ stations: Record<string, BuoyStation> }> = ({ stations }) => {
  const { locationId } = useParams();
  const [forecastData, setForecastData] = useState<ForecastData | null>(null);
  const [locationName, setLocationName] = useState<string | null>(null); // Track the station name


  useEffect(() => {
    if (!locationId) return;

    // Fetch forecast data and location name when locationId changes
    (async function () {
      try {
        const response = await fetch(`/api/forecast/${locationId}`);
        const data = await response.json();
        setForecastData(data);

        const name = stations[locationId]?.name || 'Unknown Station';
        setLocationName(name); // Set the location name
      } catch (err) {
        console.error('Error fetching data:', err);
      }
    })();
  }, [locationId, stations]); // Include stations in dependency array in case they change

  // Handle the case where no forecastData or locationName exists
  if (!locationId) return <div>No location specified</div>;
  if (!forecastData) return <div>Loading forecast...</div>;


  // check for forecast

  return (
    <div id="main-container">
      <div className="forecast_header">
        <a href="/" className="wave_and_weather_title">
          Surf Forecast
        </a>
        <p className="title_form_text">{locationName}</p>

        <LocationForm stations={stations} />
      </div>

      <div className="individual_data_fields">
        <div className="wave_wind_air">
          <div className="wave_data_fields">
            <div className="wave_height_layout">
              <p className="wave_height">
                {forecastData ? `${forecastData.current_wave_height} ${forecastData.units}` : "Loading..."}
              </p>
              <p className="current_wave_height_text" id="current_wave_height">
                Wave Height
              </p>
            </div>
          </div>

          <div className="wind_data_fields">
            <div className="wind_layout">
              <p className="data">{forecastData ? forecastData.wind_speed : "Loading..."}</p>
              <p className="label">Wind Speed</p>
            </div>
            <div className="wind_layout">
              <p className="data">{forecastData ? forecastData.wind_direction : "Loading..."}</p>
              <p className="label">Wind Direction</p>
            </div>
          </div>

          <div className="general_weather_data_fields">
            <div className="forecast_layout">
              <p className="data">{forecastData ? forecastData.short_forecast : "Loading..."}</p>
              <p className="label">Forecast</p>
            </div>
            <div className="forecast_layout">
              <p className="data">{forecastData ? forecastData.air_temperature : "Loading..."}</p>
              <p className="label">Air Temperature</p>
            </div>
          </div>
        </div>

        <div className="alerts_layout">
          <p className="data">{forecastData ? forecastData.weather_alerts : "Loading..."}</p>
          <p className="label">Current Weather Warnings</p>
        </div>
      </div>

      <p className="wave_height_graph_label">Wave Height</p>
      <div className="wave_height_graph">
        {forecastData ? (
          <img src={`data:image/png;base64,${forecastData.wave_height_graph}`} alt="Wave Height Graph" />
        ) : (
          "Loading..."
        )}
      </div>
    </div>
  );
};


// (condition ? ifTrue : ifFalse)