import type Plotly from "plotly.js-basic-dist";
import React, { useCallback, useMemo } from "react";
import { HourlyForecast } from "./api";
import { useUnits } from "./Units";

interface WaveChartProps {
  hourlyForecast: HourlyForecast[];
}

const PlotlyGraph = React.lazy(() => import("./PlotlyGraph"));

const WaveChart: React.FC<WaveChartProps> = ({ hourlyForecast = [] }) => {
  const units = useUnits();
  const plotData = useMemo<Plotly.Data[]>(() => {
    if (!hourlyForecast || hourlyForecast.length === 0) {
      return [];
    }

    const times = hourlyForecast.map((h) => h.date_time_stamp);
    return [
      {
        x: times,
        y: hourlyForecast.map((h) =>
          units.distance.convert(h.max_breaking_height)
        ),
        type: "scatter",
        mode: "lines", // Removed the 'markers' to only show lines
        name: "Breaking Wave Height",
        line: { color: "#00b894", shape: "spline" },
      },
      {
        x: times,
        y: hourlyForecast.map((h) => units.distance.convert(h.wave_height)),
        type: "scatter",
        mode: "lines",
        name: "Swell Height",
        line: { color: "#e17055", shape: "spline" },
      },
    ];
  }, [hourlyForecast, units]);

  const plotLayout = useCallback(
    (isMobile: boolean): Partial<Plotly.Layout> => ({
      width: hourlyForecast.length * 50,
      xaxis: {
        title: "Time",
        titlefont: { size: 18, family: "Arial, sans-serif", color: "#636e72" },
        tickfont: { size: 14, family: "Arial, sans-serif", color: "#636e72" },
        showgrid: false, // Hide the grid lines
        zeroline: false,
      },
      yaxis: {
        title: `Wave Height (${units.distance.name})`,
        ticksuffix: ` ${units.distance.name}  `,
        titlefont: { size: 18, family: "Arial, sans-serif", color: "#636e72" },
        tickfont: { size: 14, family: "Arial, sans-serif", color: "#636e72" },
        showgrid: true,
        gridcolor: "#ddd",
      },
      hovermode: "closest",
      showlegend: true,
      legend: {
        orientation: "h", // Horizontal layout
        x: 0, // Center horizontally
        y: -0.2, // Move below the x-axis (adjust as needed)
        xanchor: "left",
        yanchor: "bottom",
        font: { family: "Inter", size: 14, color: "#636e72" },
      },
      margin: {
        l: 80,
        r: 30,
        t: 50,
        b: 30,
      },
      autosize: true,
      plot_bgcolor: "#f4f6f7",
      paper_bgcolor: "#ffffff",
    }),
    [units]
  );

  // Ensure graph_data is not empty before proceeding
  if (plotData.length === 0) {
    return <p>No forecast data available</p>;
  }

  return (
    <React.Suspense fallback={null}>
      <div style={{ overflowX: "auto", width: "80%", marginBottom: "150px" }}>
        <PlotlyGraph data={plotData} layout={plotLayout} />
      </div>
    </React.Suspense>
  );
};

export default WaveChart;
