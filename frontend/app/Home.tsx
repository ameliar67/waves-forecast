import React from "react";
import { LocationForm } from "./LocationForm";

const LocationMap = React.lazy(() =>
  import("./LocationMap").then((m) => ({ default: m.LocationMap }))
);

export const HomePage: React.FC = () => (
  <>
    <div id="header">
      <p className="landing-page-title">Surf Forecast</p>
      <LocationForm />
    </div>

    <React.Suspense fallback={null}>
      <LocationMap className={"home-map"} />
    </React.Suspense>
  </>
);
