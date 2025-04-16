import React, { useEffect, useRef } from "react";
import {
  createChart,
  CrosshairMode
} from "lightweight-charts";

const CandlestickChart = ({ data }) => {
  const chartContainerRef = useRef();
  const chartRef = useRef();
  const candlestickSeriesRef = useRef();

  useEffect(() => {
    chartRef.current = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 400,
      layout: {
        background: { color: "transparent" },
        textColor: "#ccc",
      },
      grid: {
        vertLines: { color: "#444" },
        horzLines: { color: "#444" },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
      },
      priceScale: {
        borderVisible: false,
      },
      timeScale: {
        borderVisible: false,
        timeVisible: true,
      },
    });

    candlestickSeriesRef.current = chartRef.current.addCandlestickSeries();

    // Cleanup on unmount
    return () => chartRef.current.remove();
  }, []);

  useEffect(() => {
    if (data && data.length) {
      candlestickSeriesRef.current.setData(data);
    }
  }, [data]);

  return <div ref={chartContainerRef} className="w-full" />;
};

export default CandlestickChart;
