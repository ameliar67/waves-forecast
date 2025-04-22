import { useEffect, useState } from "react";
import { BrowserRouter, Route, Routes } from "react-router";
import { BuoyStation, getLocations } from "./api";
import { ForecastPage } from "./ForecastPage";
import { HomePage } from "./Home";
import { StationsContext } from "./Stations";
import { ImperialConversions, MetricConversions, UnitsContext } from "./Units";

export function App() {
  const [stations, setStations] = useState<Record<string, BuoyStation>>({});
  const [unitSystem, setUnitSystem] = useState<"metric" | "imperial">(
    "imperial"
  );

  // Fetch locations from the backend API when the component loads
  useEffect(() => {
    getLocations()
      .then((l) => setStations(l))
      .catch((err) => console.error("Error fetching station data:", err));
  }, []);

  return (
    <UnitsContext.Provider
      value={unitSystem === "metric" ? MetricConversions : ImperialConversions}
    >
      <StationsContext.Provider value={stations}>
        <BrowserRouter>
          <Routes>
            <Route index element={<HomePage />} />
            <Route path="/forecast/:locationId" element={<ForecastPage />} />
          </Routes>
        </BrowserRouter>
      </StationsContext.Provider>
    </UnitsContext.Provider>
  );
}
