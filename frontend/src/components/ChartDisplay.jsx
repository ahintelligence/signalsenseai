import { useEffect } from "react";
import { createChart, CrosshairMode } from "lightweight-charts";

export default function ChartDisplay({
  chartRef,
  candleData = [],
  smaData = [],
  emaSeries = [],
  rsiData = [],
  showSMA,
  showRSI,
  enlarged,
  darkMode,
  histError,
}) {
  useEffect(() => {
    if (!chartRef.current || candleData.length === 0) return;

    // Clear previous chart
    chartRef.current.innerHTML = "";

    const width = chartRef.current.clientWidth;
    const height = chartRef.current.clientHeight;

    // Create chart with dynamic size
    const chart = createChart(chartRef.current, {
      width,
      height,
      layout: {
        background: { color: darkMode ? "#0f172a" : "#ffffff" },
        textColor: darkMode ? "#e2e8f0" : "#1e293b",
      },
      grid: {
        vertLines: { color: darkMode ? "#374151" : "#e5e7eb" },
        horzLines: { color: darkMode ? "#374151" : "#e5e7eb" },
      },
      crosshair: { mode: CrosshairMode.Normal },
      rightPriceScale: { borderColor: darkMode ? "#475569" : "#cbd5e1" },
      timeScale: { borderColor: darkMode ? "#475569" : "#cbd5e1" },
    });

    // Candlestick series
    chart
      .addCandlestickSeries({
        upColor: "#16a34a",
        downColor: "#dc2626",
        borderUpColor: "#16a34a",
        borderDownColor: "#dc2626",
        wickUpColor: "#16a34a",
        wickDownColor: "#dc2626",
      })
      .setData(candleData);

    // SMA overlay
    if (showSMA && smaData.length) {
      chart.addLineSeries({ color: "#f59e0b", lineWidth: 2 }).setData(smaData);
    }

    // EMA overlays
    emaSeries.forEach(({ key, data }) => {
      if (data.length) {
        const colorMap = {
          ema9: "#f97316",
          ema20: "#3b82f6",
          ema50: "#10b981",
          ema100: "#ec4899",
          ema200: "#8b5cf6",
        };
        chart
          .addLineSeries({ color: colorMap[key] || "#999", lineWidth: 2 })
          .setData(data);
      }
    });

    // RSI overlay in bottom 20%
    if (showRSI && rsiData.length) {
      chart
        .addLineSeries({
          color: "#a3e635",
          lineWidth: 1,
          priceScaleId: "",
          scaleMargins: { top: 0.8, bottom: 0 },
        })
        .setData(rsiData);
    }

    chart.timeScale().fitContent();
    return () => chart.remove();
  }, [
    candleData,
    smaData,
    emaSeries,
    rsiData,
    showSMA,
    showRSI,
    darkMode,
    enlarged,
  ]);

  return (
    <div
      className={`w-full h-full transition-all duration-500 ${
        darkMode ? "bg-zinc-900 text-zinc-200" : "bg-white text-zinc-800"
      }`}
      style={{
        border: "1px solid",
        borderColor: darkMode ? "#475569" : "#cbd5e1",
        borderRadius: "4px",
      }}
    >
      {histError && <p className="text-red-400 p-4">Error: {histError}</p>}
      <div ref={chartRef} className="w-full h-full" />
    </div>
  );
}











