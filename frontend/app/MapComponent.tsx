"use client";

import React from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import MarkerCluster from "react-leaflet-markercluster";
import { LatLngExpression } from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet-defaulticon-compatibility";
import "leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.css";
import "react-leaflet-markercluster/dist/styles.min.css";

interface BuoyStation {
  latitude: number;
  longitude: number;
  name: string;
}

interface MapComponentProps {
  stations: { [key: string]: BuoyStation };
}

const center: LatLngExpression = [21.505, -25.09];

export const MapComponent: React.FC<MapComponentProps> = ({ stations }) => {
  const zoom = 2.5;

  return (
    <div style={{ position: "relative", height: "400px", width: "100%" }}>
      <MapContainer
        center={center}
        zoom={zoom}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

        <MarkerCluster>
          {Object.entries(stations).map(([locId, buoyStation]) => (
            <Marker
              key={locId}
              position={[buoyStation.latitude, buoyStation.longitude]}
            >
              <Popup>
                <div>
                  <a href={`/forecast/${locId}`}>{buoyStation.name}</a>
                </div>
              </Popup>
            </Marker>
          ))}
        </MarkerCluster>
      </MapContainer>
    </div>
  );
};
