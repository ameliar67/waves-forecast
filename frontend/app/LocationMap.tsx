import { LatLngExpression } from "leaflet";
import "leaflet-defaulticon-compatibility";
import "leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.css";
import "leaflet/dist/leaflet.css";
import React, { useMemo } from "react";
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import MarkerCluster from "react-leaflet-markercluster";
import "react-leaflet-markercluster/dist/styles.min.css";
import { useStations } from "./Stations";
import L from "leaflet";

interface MapComponentProps {
  className?: string;
}

const center: LatLngExpression = [30.5, -95.5];

export const LocationMap: React.FC<MapComponentProps> = ({ className }) => {
  const stationsMap = useStations();
  const stations = useMemo(() => Object.values(stationsMap), [stationsMap]);

  return (
    <MapContainer
      className={className}
      center={center}
      zoom={3}
      minZoom={3}
      maxBounds={[
        [-170, -240],
        [110, 210],
      ]}
      maxBoundsViscosity={1.0}
      worldCopyJump={false}
    >
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

      <MarkerCluster
        iconCreateFunction={(cluster: any) => {
          const count = cluster.getChildCount();

          return L.divIcon({
            html: `<div>${count}</div>`,
            className: "custom-cluster-icon",
            iconSize: [40, 40],
          });
        }}
      >
        {stations.map((beachLocation) => (
          <Marker
            key={beachLocation.id}
            position={[
              beachLocation.beach_latitude,
              beachLocation.beach_longitude,
            ]}
          >
            <Popup closeButton={false}>
              <div>
                <a href={`/forecast/${encodeURIComponent(beachLocation.id)}`}>
                  {beachLocation.name}
                </a>
              </div>
            </Popup>
          </Marker>
        ))}
      </MarkerCluster>
    </MapContainer>
  );
};
