import React from "react";
import { TidalForecast } from "./api";

interface TidesProps {
  tidalForecast: TidalForecast[];
}

const TideGraph: React.FC<TidesProps> = ({ tidalForecast }) => {
  if (!tidalForecast || tidalForecast.length === 0) {
    return null;
  }

  const pointSpacing = 180;
  const width = tidalForecast.length * pointSpacing * 2;
  const height = 500;
  const padding = 80;

  const graphMinY = 10;
  const graphMaxY = 370;

  // Simulate tide height variation
  const processed = tidalForecast.map((d, i) => {
    const base = d.tidal_event.toLowerCase() === "h" ? 2 : 1;

    const normalized = (base - 1) / (2.4 - 1); // simulate 1–2.4 range
    const y = graphMaxY - normalized * (graphMaxY - graphMinY);
    const date = new Date(d.date);

    return {
      x: (i / (tidalForecast.length - 1)) * (width - 2 * padding) + padding,
      y,
      date_label: date.toLocaleDateString([], {}),
      time_label: date.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
      event: d.tidal_event,
    };
  });

  // Smooth curve builder
  const buildSmoothPath = (points: { x: number; y: number }[]) => {
    if (points.length < 2) return "";

    const result = [`M ${points[0].x},${points[0].y}`];

    for (let i = 0; i < points.length - 1; i++) {
      const p0 = points[i - 1] || points[i];
      const p1 = points[i];
      const p2 = points[i + 1];
      const p3 = points[i + 2] || p2;

      // Catmull-Rom to Bézier conversion formula
      const cp1x = p1.x + (p2.x - p0.x) / 6;
      const cp1y = p1.y + (p2.y - p0.y) / 6;
      const cp2x = p2.x - (p3.x - p1.x) / 6;
      const cp2y = p2.y - (p3.y - p1.y) / 6;

      result.push(`C ${cp1x},${cp1y} ${cp2x},${cp2y} ${p2.x},${p2.y}`);
    }

    return result.join(" ");
  };

  const pathD = buildSmoothPath(processed);

  return (
    <div id="tide-container">
      <p id="tides-text">Tides</p>
      <svg width={width} height={height} overflow="scroll">
        {/* Tide curve */}
        <path d={pathD} fill="none" stroke="#137479" strokeWidth="3" />

        {/* Dots and Labels */}
        {processed.map((p, i) => (
          <g key={i}>
            {/* Vertical line and event label */}
            <>
              <line
                x1={p.x}
                y1={p.y}
                x2={p.x}
                y2={height - 60}
                stroke="#6fb8af"
                strokeWidth="7"
              />
              {/* Event label (High or Low) */}
              <text
                x={p.x}
                // Check if it's high or low tide and place the label above accordingly
                y={p.event.toLowerCase() === "h" ? p.y - 35 : p.y - 25} // High tide is above the peak, low tide is above the trough
                textAnchor="middle"
                fontSize="18"
                fill="#000"
              >
                {p.event}
              </text>

              {/* Date and time labels */}
              <text
                x={p.x}
                y={height - 20}
                textAnchor="middle"
                fontSize="18"
                fill="#555"
              >
                {p.date_label}
              </text>
              <text
                x={p.x}
                y={height - 40}
                textAnchor="middle"
                fontSize="14"
                fill="#555"
              >
                {p.time_label}
              </text>
            </>
          </g>
        ))}
      </svg>
    </div>
  );
};

export default TideGraph;
