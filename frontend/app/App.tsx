import { useEffect, useState } from "react";
import { BrowserRouter, Route, Routes } from "react-router";
import { ForecastPage } from "./ForecastPage";
import { HomePage } from "./Home";
import { BuoyStation, getLocations } from "./api";

export function App() {
  const [stations, setStations] = useState<Record<string, BuoyStation>>({});

  // Fetch locations from the backend API when the component loads
  useEffect(() => {
    getLocations()
      .then((l) => setStations(l))
      .catch((err) => console.error("Error fetching station data:", err));
  }, []);

  return (
    <BrowserRouter>
      <Routes>
        <Route index element={<HomePage stations={stations} />} />
        <Route
          path="/forecast/:locationId"
          element={<ForecastPage stations={stations} />}
        />
      </Routes>
    </BrowserRouter>
  );
}
