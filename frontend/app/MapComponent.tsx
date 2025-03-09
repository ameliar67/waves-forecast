import { LatLngExpression } from "leaflet";
import "leaflet-defaulticon-compatibility";
import "leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.css";
import "leaflet/dist/leaflet.css";
import React from "react";
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import MarkerCluster from "react-leaflet-markercluster";
import "react-leaflet-markercluster/dist/styles.min.css";
import { BuoyStation } from "./api";

interface MapComponentProps {
  className?: string;
  stations: Record<string, BuoyStation>;
}

const center: LatLngExpression = [21.505, -25.09];

export const MapComponent: React.FC<MapComponentProps> = ({
  className,
  stations,
}) => {
  return (
    <MapContainer className={className} center={[30.5, -95.5]} zoom={2.5}>
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
  );
};
