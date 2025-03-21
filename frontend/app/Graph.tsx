import React, { useEffect, useRef } from "react";

interface HourlyForecast {
  max_breaking_height: number;
  min_breaking_height: number;
  wave_height: number;
  date: string;
}

interface ForecastData {
  hourly_forecast: HourlyForecast[];
}

interface WaveChartProps {
  forecastData: ForecastData;
}

const WaveChart: React.FC<WaveChartProps> = ({ forecastData }) => {
  const { hourly_forecast } = forecastData;
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    if (!canvasRef.current || hourly_forecast.length === 0) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const paddingLeft = 170, paddingTop = 50, canvasWidth = canvas.width - paddingLeft - 50, canvasHeight = canvas.height - paddingTop - 50;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const times = hourly_forecast.map(({ date }) => date);
    const maxs = hourly_forecast.map(({ max_breaking_height }) => max_breaking_height);
    const mins = hourly_forecast.map(({ min_breaking_height }) => min_breaking_height);
    const waveHeight = hourly_forecast.map(({ wave_height }) => wave_height);
    const allValues = [...maxs, ...mins, ...waveHeight];
    const yMax = Math.max(...allValues);
    const yMin = Math.min(...allValues);
    const yRange = yMax - yMin;

    const drawLine = (data: number[], color: string) => {
      ctx.beginPath();
      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      data.forEach((value, index) => {
        const x = (index * canvasWidth) / (times.length - 1) + paddingLeft;
        const y = canvasHeight - ((value - yMin) / yRange) * canvasHeight + paddingTop;
        index === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
      });
      ctx.stroke();
    };

    const formatDate = (dateStr: string) =>
      new Date(dateStr).toLocaleString("en-US", {
        weekday: "short", year: "numeric", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", hour12: true
      });

    const drawTicksAndLabels = () => {
      ctx.fillStyle = "#636e72";
      ctx.font = "14px Arial";
      
      times.forEach((time, index) => {
        if (index % 3 === 0) {
          const x = (index * canvasWidth) / (times.length - 1) + paddingLeft;
          ctx.fillText(formatDate(time), x - 45, canvasHeight + paddingTop + 35);
          ctx.beginPath();
          ctx.moveTo(x, canvasHeight + paddingTop);
          ctx.lineTo(x, canvasHeight + paddingTop + 10);
          ctx.strokeStyle = "#636e72"; // Set the tick color explicitly
          ctx.stroke();
        }
      });

      const yStep = yRange / 5;
      for (let i = 0; i <= 5; i++) {
        const y = canvasHeight - ((yMin + i * yStep - yMin) / yRange) * canvasHeight + paddingTop;
        ctx.fillText((yMin + i * yStep).toFixed(1), paddingLeft - 50, y);
        ctx.beginPath();
        ctx.moveTo(paddingLeft - 5, y);
        ctx.lineTo(paddingLeft, y);
        ctx.strokeStyle = "#636e72"; // Set the tick color explicitly
        ctx.stroke();
      }

      ctx.save();
      ctx.translate(paddingLeft / 2 - 20, canvasHeight / 2 + paddingTop);
      ctx.rotate(-Math.PI / 2);
      ctx.fillText("Wave Height (feet)", 0, 0);
      ctx.restore();
      ctx.fillText("Time", canvasWidth / 2 + paddingLeft, canvasHeight + paddingTop + 70);
    };

    drawLine(maxs, "#00b894");
    drawLine(mins, "#0984e3");
    drawLine(waveHeight, "#e17055");
    drawTicksAndLabels();
  }, [hourly_forecast]);

  return (
    <div className="graph">
      <canvas ref={canvasRef} width={1500} height={700} />
    </div>
  );
};

export default WaveChart;
