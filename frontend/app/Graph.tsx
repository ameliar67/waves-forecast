import Plotly from "plotly.js-basic-dist";
import React, { useLayoutEffect, useMemo, useRef, useState } from "react";

interface HourlyForecast {
  max_breaking_height: number;
  min_breaking_height: number;
  wave_height: number;
  date: string; // ISO 8601 date format
}

interface ForecastData {
  hourly_forecast: HourlyForecast[];
}

interface WaveChartProps {
  forecastData: ForecastData;
}

const WaveChart: React.FC<WaveChartProps> = ({ forecastData }) => {
  const { hourly_forecast = [] } = forecastData;

  const [isMobile, setIsMobile] = useState(false);
  useLayoutEffect(() => {
    const match = window.matchMedia("(min-width:768px)");
    setIsMobile(match.matches);

    const listener = (e: MediaQueryListEvent) => setIsMobile(e.matches);
    match.addEventListener("change", listener);
    return () => match.removeEventListener("change", listener);
  }, []);

  const plotData = useMemo<Plotly.Data[]>(() => {
    if (!hourly_forecast || hourly_forecast.length === 0) {
      return [];
    }

    const times = hourly_forecast.map((h) => h.date);
    return [
      {
        x: times,
        y: hourly_forecast.map((h) => h.max_breaking_height),
        type: "scatter",
        mode: "lines", // Removed the 'markers' to only show lines
        name: "Max Breaking Wave Height",
        line: { color: "#00b894", shape: "spline" },
      },
      {
        x: times,
        y: hourly_forecast.map((h) => h.min_breaking_height),
        type: "scatter",
        mode: "lines",
        name: "Min Breaking Wave Height",
        line: { color: "#0984e3", shape: "spline" },
      },
      {
        x: times,
        y: hourly_forecast.map((h) => h.wave_height),
        type: "scatter",
        mode: "lines",
        name: "Wave Height",
        line: { color: "#e17055", shape: "spline" },
      },
    ];
  }, [hourly_forecast]);

  const plotLayout = useMemo<Partial<Plotly.Layout>>(
    () => ({
      xaxis: {
        title: "Time",
        titlefont: { size: 18, family: "Arial, sans-serif", color: "#636e72" },
        tickfont: { size: 14, family: "Arial, sans-serif", color: "#636e72" },
        showgrid: false, // Hide the grid lines
        zeroline: false,
      },
      yaxis: {
        title: "Wave Height (feet)",
        titlefont: { size: 18, family: "Arial, sans-serif", color: "#636e72" },
        tickfont: { size: 14, family: "Arial, sans-serif", color: "#636e72" },
        showgrid: true,
        gridcolor: "#ddd",
      },
      hovermode: "closest",
      showlegend: true,
      legend: {
        x: isMobile ? 0.5 : 0.5, // Center the legend horizontally on mobile and desktop
        y: isMobile ? 1.1 : 1.05,
        xanchor: "center", // Center the legend horizontally
        yanchor: "bottom", // Align to the bottom of the legend box
        orientation: "v",
        font: { family: "Inter", size: 14, color: "#636e72" },
      },
      margin: {
        l: 50,
        r: 30,
        t: 50,
        b: 100,
      },
      autosize: true,
      plot_bgcolor: "#f4f6f7",
      paper_bgcolor: "#ffffff",
    }),
    [isMobile]
  );

  const graphElement = useRef<HTMLDivElement | null>(null);

  useLayoutEffect(() => {
    if (graphElement.current) {
      Plotly.newPlot(graphElement.current, plotData, plotLayout);
    }
  }, [plotData, plotLayout]);

  // Ensure graph_data is not empty before proceeding
  if (plotData.length === 0) {
    return <p>No graph data available</p>;
  }

  return <div className="graph" ref={graphElement}></div>;
};

export default WaveChart;
