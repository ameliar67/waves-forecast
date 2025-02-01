import React, { useEffect, useState } from "react";

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

  // Styles for the progress bar container
  const containerStyles: React.CSSProperties = {
    height: containerHeight,
    width: "80%", 
    backgroundColor: "white",
    overflow: "hidden",
    position: "relative",
  };

  // Styles for the filler (progress) part of the bar
  const fillerStyles: React.CSSProperties = {
    height: "100%",
    width: "100%",
    position: "absolute", 
    top: 0,
    left: `${position}%`,
    backgroundColor: "#e3e3e3",
  };

  return (
    <div style={containerStyles}>
      <div style={fillerStyles}></div>
    </div>
  );
};

export default ProgressBar;
