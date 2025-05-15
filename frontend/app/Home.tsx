import React from "react";
import { LocationForm } from "./LocationForm";

const logo = new URL("./surf-logo.svg", import.meta.url) as unknown as string;

const LocationMap = React.lazy(() =>
  import("./LocationMap").then((m) => ({ default: m.LocationMap }))
);

export const HomePage: React.FC = () => {
  return (
    <>
      <div id="header">
        <div id="title-block">
          <img id="surf-logo" src={logo} alt="Surf Logo" />
          <p className="landing-page-title">Surf Sage</p>
        </div>
        <LocationForm />
      </div>

      <React.Suspense fallback={null}>
        <LocationMap className={"home-map"} />
      </React.Suspense>
    </>
  );
};
