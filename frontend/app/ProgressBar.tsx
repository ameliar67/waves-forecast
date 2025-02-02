import React, { useEffect, useState } from "react";
import "./ProgressBar.css";  // Import the CSS file for styling

interface ProgressBarProps {
  containerHeight: number | string;
}

const ProgressBar: React.FC<ProgressBarProps> = ({ containerHeight }) => {
  const [position, setPosition] = useState<number>(-100);

  useEffect(() => {
    // Update the position of the filler to create the indeterminate animation
    const interval = setInterval(() => {
      setPosition((prevPosition) => (prevPosition >= 100 ? -100 : prevPosition + 2));
    }, 30);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="progress-container" style={{ height: containerHeight }}>
      <div className="progress-filler" style={{ left: `${position}%` }}></div>
    </div>
  );
};

export default ProgressBar;
