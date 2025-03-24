import React from "react";
import { BuoyStation } from "./api";
import { LocationForm } from "./LocationForm";

const LocationMap = React.lazy(() =>
  import("./LocationMap").then((m) => ({ default: m.LocationMap }))
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
      <LocationMap className={"home-map"} stations={stations} />
    </React.Suspense>
  </>
);
