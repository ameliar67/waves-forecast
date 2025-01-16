"use client";

import React from "react";
import { LocationForm } from "./LocationForm";
import { MapComponent } from "./MapComponent";
import { BuoyStation } from "./LocationData";

export const HomePage: React.FC<{ stations: Record<string, BuoyStation> }> = ({
  stations,
}) => (
  <div className="landing_page">
    <div id="main-container">
      <div id="header">
        <p className="landing_page_title">Surf Forecast</p>
        <LocationForm stations={stations} />
      </div>

      <MapComponent stations={stations} />
    </div>
  </div>
);
