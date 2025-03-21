import React, { useEffect, useState } from "react";
import Plot from "react-plotly.js";

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

  // Check the screen size on component mount and on window resize
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 768);
    };
    handleResize();
    window.addEventListener("resize", handleResize);

    return () => window.removeEventListener("resize", handleResize);
  }, []);

  // Ensure graph_data is not empty before proceeding
  if (!hourly_forecast || hourly_forecast.length === 0) {
    return <p>No graph data available</p>;
  }

  const times: string[] = [];
  const maxs: number[] = [];
  const mins: number[] = [];
  const wave_height: number[] = [];

  hourly_forecast.forEach((data) => {
    times.push(data.date);
    maxs.push(data.max_breaking_height);
    mins.push(data.min_breaking_height);
    wave_height.push(data.wave_height);
  });

  const plotData: Plotly.Data[] = [
    {
      x: times,
      y: maxs,
      type: "scatter",
      mode: "lines", // Removed the 'markers' to only show lines
      name: "Max Breaking Wave Height",
      line: { color: "#00b894" },
    },
    {
      x: times,
      y: mins,
      type: "scatter",
      mode: "lines",
      name: "Min Breaking Wave Height",
      line: { color: "#0984e3" },
    },
    {
      x: times,
      y: wave_height,
      type: "scatter",
      mode: "lines",
      name: "Wave Height",
      line: { color: "#e17055" },
    },
  ];

  const plotLayout: Partial<Plotly.Layout> = {
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
  };

  return (
    <div className="graph">
      <Plot
        data={plotData}
        layout={plotLayout}
        config={{
          responsive: true, // Make the plot responsive to window resizing
        }}
        style={{ width: "100%", height: "100%" }}
      />
    </div>
  );
};

export default WaveChart;
