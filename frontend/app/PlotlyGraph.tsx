import Plotly from "plotly.js-basic-dist";
import React, { useLayoutEffect, useMemo, useRef, useState } from "react";

interface PlotlyGraphProps {
  data: Plotly.Data[];
  layout: (isMobile: boolean) => Partial<Plotly.Layout>;
}

const PlotlyGraph: React.FC<PlotlyGraphProps> = ({ data, layout }) => {
  const [isMobile, setIsMobile] = useState(false);
  useLayoutEffect(() => {
    const match = window.matchMedia("(min-width:768px)");
    setIsMobile(match.matches);

    const listener = (e: MediaQueryListEvent) => setIsMobile(e.matches);
    match.addEventListener("change", listener);
    return () => match.removeEventListener("change", listener);
  }, []);

  const graphElement = useRef<HTMLDivElement | null>(null);
  const plotLayout = useMemo(() => layout(isMobile), [layout, isMobile]);

  useLayoutEffect(() => {
    if (graphElement.current) {
      Plotly.newPlot(graphElement.current, data, plotLayout);
    }
  }, [data, plotLayout]);

  return !data?.length ? null : <div className="graph" ref={graphElement} />;
};

export default PlotlyGraph;
