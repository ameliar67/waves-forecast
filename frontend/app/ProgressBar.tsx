import React, { useEffect, useState } from "react";

interface ProgressBarProps {
  containerHeight: number | string;
}

const ProgressBar: React.FC<ProgressBarProps> = ({ containerHeight }) => {
  const [position, setPosition] = useState<number>(-100);

  useEffect(() => {
    // Update the position of the filler to create the indeterminate animation
    const interval = setInterval(() => {
      setPosition((prevPosition) =>
        prevPosition >= 100 ? -100 : prevPosition + 0.2
      );
    }, 1);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="progress-container" style={{ height: containerHeight }}>
      <div className="progress-filler" style={{ left: `${position}%` }}></div>
    </div>
  );
};

export default ProgressBar;
