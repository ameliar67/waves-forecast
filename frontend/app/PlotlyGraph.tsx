import Plotly from "plotly.js-basic-dist";
import React, { useLayoutEffect, useMemo, useRef } from "react";
import { useIsMobile } from "./mobile";

interface PlotlyGraphProps {
  data: Plotly.Data[];
  layout: (isMobile: boolean) => Partial<Plotly.Layout>;
}

const PlotlyGraph: React.FC<PlotlyGraphProps> = ({ data, layout }) => {
  const isMobile = useIsMobile();
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
