import React from "react";
import { BuoyStation } from "./api";
import { LocationForm } from "./LocationForm";

const MapComponent = React.lazy(() =>
  import("./MapComponent").then((m) => ({ default: m.MapComponent }))
);

export const HomePage: React.FC<{ stations: Record<string, BuoyStation> }> = ({
  stations,
}) => (
  <>
    <div id="header">
      <p className="landing-page-title">Surf Forecast</p>
      <LocationForm stations={stations} />
    </div>

    <React.Suspense fallback={null}>
      <MapComponent className={"home-map"} stations={stations} />
    </React.Suspense>
  </>
);
