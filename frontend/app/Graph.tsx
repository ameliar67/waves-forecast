import React from "react";
import Plot from "react-plotly.js";

interface GraphData {
  maxs: number;
  mins: number;
  hourly_summary: number;
  date: string; // ISO 8601 date format
}

interface ForecastData {
  hourly_forecast: GraphData[];
}

interface WaveChartProps {
  forecastData: ForecastData;
}

const WaveChart: React.FC<WaveChartProps> = ({ forecastData }) => {
  const { hourly_forecast = [] } = forecastData;

  // Ensure graph_data is not empty before proceeding
  if (!hourly_forecast || hourly_forecast.length === 0) {
    return <p>No graph data available</p>;
  }

  // Extract data for plotting by iterating over the array of objects
  const times: string[] = [];
  const maxs: number[] = [];
  const mins: number[] = [];
  const summary: number[] = [];

  hourly_forecast.forEach((data) => {
    times.push(data.date);
    maxs.push(data.maxs);
    mins.push(data.mins);
    summary.push(data.hourly_summary);
  });

  // Define the Plot data structure with lines only (no markers)
  const plotData: Plotly.Data[] = [
    {
      x: times,
      y: maxs,
      type: "scatter",
      mode: "lines", // Removed the 'markers' to only show lines
      name: "Max Wave Height",
      line: { color: "green" },
    },
    {
      x: times,
      y: mins,
      type: "scatter",
      mode: "lines",
      name: "Min Wave Height",
      line: { color: "blue" },
    },
    {
      x: times,
      y: summary,
      type: "scatter",
      mode: "lines",
      name: "Wave Summary",
      line: { color: "red" },
    },
  ];

  const plotLayout: Partial<Plotly.Layout> = {
    title: {
      text: "Hourly Wave Height",
      font: { size: 24, family: "Inter", color: "black" },
    },
    xaxis: {
      title: "Time",
      titlefont: { size: 18, family: "Arial, sans-serif", color: "black" },
      tickfont: { size: 14, family: "Arial, sans-serif", color: "black" },
    },
    yaxis: {
      title: "Wave Height (feet)",
      titlefont: { size: 18, family: "Arial, sans-serif", color: "black" },
      tickfont: { size: 14, family: "Arial, sans-serif", color: "black" },
    },
    hovermode: "closest", // Correct value for hovermode
    plot_bgcolor: "#f7f7f7", // Light background color
    paper_bgcolor: "#f7f7f7", // Light paper background color
    showlegend: true,
    margin: {
      l: 50, // Left margin
      r: 50, // Right margin
      t: 50, // Top margin
      b: 50, // Bottom margin
    },
  };

  return (
    <div style={{ width: "1300px", height: "500px", marginBottom: "70px" }}>
      <Plot
        data={plotData}
        layout={plotLayout}
        config={{
          staticPlot: true, // Disable interactivity
        }}
        style={{ width: "100%", height: "100%" }}
      />
    </div>
  );
};

export default WaveChart;
