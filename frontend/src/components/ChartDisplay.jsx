// src/components/ChartDisplay.jsx
import { useEffect } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip as RechartsTooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";
import { createChart } from "lightweight-charts";

export default function ChartDisplay({
  chartRef,
  showCandles,
  darkMode,
  lineChartData,
  showSMA,
  showEMAs,
  showRSI,
  priceData,
  histError,
}) {
    useEffect(() => {
        if (!showCandles || !chartRef.current) return;
      
        chartRef.current.innerHTML = "";
      
        const chart = createChart(chartRef.current, {
          layout: {
            background: { color: darkMode ? "#111827" : "#f3f4f6" },
            textColor: darkMode ? "#f3f4f6" : "#111827",
          },
          grid: {
            vertLines: { color: darkMode ? "#374151" : "#e5e7eb" },
            horzLines: { color: darkMode ? "#374151" : "#e5e7eb" },
          },
          width: chartRef.current.clientWidth,
          height: 250,
          crosshair: { mode: 0 },
        });
      
        const candleData = priceData
          .map(d => ({
            time: Math.floor(new Date(d.date).getTime() / 1000),
            open: +d.open,
            high: +d.high,
            low: +d.low,
            close: +d.close,
          }))
          .filter(d => !isNaN(d.open));
      
        chart.addCandlestickSeries().setData(candleData);
      
        if (showSMA) {
          const smaData = priceData
            .filter(d => d.sma20 !== null && d.sma20 !== undefined && !isNaN(+d.sma20))
            .map(d => ({
              time: Math.floor(new Date(d.date).getTime() / 1000),
              value: +d.sma20,
            }));
      
          if (smaData.length > 1) {
            // Small debounce to wait for layout before drawing
            setTimeout(() => {
              chart.addLineSeries({ color: "#f59e0b", lineWidth: 2 }).setData(smaData);
            }, 100);
          }
        }
      
        Object.entries(showEMAs).forEach(([key, show]) => {
          if (show) {
            const emaData = priceData
              .filter(d => d[key] !== null && d[key] !== undefined && !isNaN(+d[key]))
              .map(d => ({
                time: Math.floor(new Date(d.date).getTime() / 1000),
                value: +d[key],
              }));
      
            if (emaData.length > 1) {
              setTimeout(() => {
                chart.addLineSeries({ color: getEmaColor(key), lineWidth: 2 }).setData(emaData);
              }, 100);
            }
          }
        });
      
        chart.timeScale().fitContent();
      
        return () => chart.remove();
      }, [priceData, showCandles, showSMA, showEMAs, darkMode]);
      

  return (
    <div className="w-full max-w-xl mt-4">
      {histError && <p className="text-red-400 mb-4">Error: {histError}</p>}

      {priceData.length > 0 && (
        <>
          {showCandles ? (
            <div ref={chartRef} className="w-full" style={{ height: 250 }} />
          ) : (
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={lineChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="Date" tick={{ fontSize: 10 }} />
                <YAxis domain={["auto", "auto"]} tick={{ fontSize: 10 }} />
                <RechartsTooltip />
                <Line
                  type="monotone"
                  dataKey="Close"
                  stroke={darkMode ? "#d1d5db" : "#374151"}
                  strokeWidth={2}
                  isAnimationActive={true}
                  animationDuration={800}
                />
                {showSMA && (
                  <Line
                    type="monotone"
                    dataKey="SMA20"
                    stroke="#f59e0b"
                    strokeWidth={2}
                    dot={false}
                    isAnimationActive={true}
                    animationDuration={800}
                  />
                )}
                {Object.entries(showEMAs).map(
                  ([k, v]) =>
                    v && (
                      <Line
                        key={k}
                        type="monotone"
                        dataKey={k}
                        stroke={getEmaColor(k)}
                        strokeWidth={2}
                        dot={false}
                        isAnimationActive={true}
                        animationDuration={800}
                      />
                    )
                )}
              </LineChart>
            </ResponsiveContainer>
          )}
        </>
      )}
    </div>
  );
}

function getEmaColor(key) {
  const map = {
    ema9: "#f97316",   // orange-500
    ema20: "#3b82f6",  // blue-500
    ema50: "#10b981",  // green-500
    ema100: "#ec4899", // pink-500
    ema200: "#8b5cf6", // violet-500
  };
  return map[key] || "#999";
}






