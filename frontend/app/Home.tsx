import React from "react";
import { BuoyStation } from "./api";
import { LocationForm } from "./LocationForm";
import { MapComponent } from "./MapComponent";

export const HomePage: React.FC<{ stations: Record<string, BuoyStation> }> = ({
  stations,
}) => (
  <>
    <div id="header">
      <p className="landing_page_title">Surf Forecast</p>
      <LocationForm stations={stations} />
    </div>

    <MapComponent className={"home-map"} stations={stations} />
  </>
);
