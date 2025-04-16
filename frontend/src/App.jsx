import React, { useState, useEffect, useRef } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { createChart } from "lightweight-charts";

export default function App() {
  // Utility functions for localStorage
  const getStored = (key, fallback) => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : fallback;
    } catch {
      return fallback;
    }
  };
  const setStored = (key, val) => {
    try { localStorage.setItem(key, JSON.stringify(val)); } catch {}
  };

  // Persistent toggle states
  const [darkMode, setDarkMode] = useState(() => getStored("darkMode", false));
  const [showCandles, setShowCandles] = useState(() => getStored("showCandles", false));
  const [showSMA, setShowSMA] = useState(() => getStored("showSMA", true));
  const [showRSI, setShowRSI] = useState(() => getStored("showRSI", false));
  const [showEMAs, setShowEMAs] = useState(() =>
    getStored("showEMAs", { ema9: false, ema20: false, ema50: false, ema100: false, ema200: false })
  );

  // Sync toggles back to localStorage
  useEffect(() => setStored("darkMode", darkMode), [darkMode]);
  useEffect(() => setStored("showCandles", showCandles), [showCandles]);
  useEffect(() => setStored("showSMA", showSMA), [showSMA]);
  useEffect(() => setStored("showRSI", showRSI), [showRSI]);
  useEffect(() => setStored("showEMAs", showEMAs), [showEMAs]);

  // Core states
  const [ticker, setTicker] = useState("");
  const [range, setRange] = useState("1mo");
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [priceData, setPriceData] = useState([]);
  const [barWidth, setBarWidth] = useState(0);
  const [animatedConfidence, setAnimatedConfidence] = useState(0);
  const [loading, setLoading] = useState(false);
  const [smaAnimatedData, setSmaAnimatedData] = useState([]);
  const [histError, setHistError] = useState(null);

  const chartContainerRef = useRef(null);
  const prevTicker = useRef("");

  const emaColorMap = {
    ema9: "#f97316",
    ema20: "#3b82f6",
    ema50: "#10b981",
    ema100: "#6366f1",
    ema200: "#ef4444",
  };

  // Fetch prediction
  const getSignal = async (symbol = ticker) => {
    if (!symbol) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch(`http://localhost:8000/predict/${symbol.toUpperCase()}`);
      const data = await res.json();
      setResult(data);
      if (!data.error) setHistory(prev => [...prev, data]);
      await fetchHistory(symbol, range);
    } catch {
      setResult({ error: "Failed to fetch signal." });
    } finally {
      setLoading(false);
    }
  };

  // Fetch history data
  const fetchHistory = async (symbol, selectedRange) => {
    try {
      const res = await fetch(
        `http://localhost:8000/history/${symbol.toUpperCase()}?range=${selectedRange}`
      );
      const json = await res.json();
      if (!res.ok) {
        setHistError(json.error || `Error ${res.status}`);
        setPriceData([]);
      } else {
        setHistError(null);
        setPriceData(json.history || []);
      }
    } catch (e) {
      setHistError(e.message);
      setPriceData([]);
    }
  };

  // Animate confidence bar
  useEffect(() => {
    if (result && !result.error && result.ticker !== prevTicker.current) {
      setBarWidth(0);
      requestAnimationFrame(() => requestAnimationFrame(() => setBarWidth(result.confidence)));
      let start = 0;
      const end = result.confidence;
      const steps = Math.ceil(900 / 25);
      const inc = end / steps;
      const timer = setInterval(() => {
        start += inc;
        setAnimatedConfidence(Math.min(end, Math.round(start)));
        if (start >= end) clearInterval(timer);
      }, 25);
      prevTicker.current = result.ticker;
      return () => clearInterval(timer);
    }
  }, [result]);

  // Refetch on range change
  useEffect(() => { if (ticker) fetchHistory(ticker, range); }, [range]);

  // Animate SMA line
  useEffect(() => {
    if (!showSMA || !priceData.length) {
      setSmaAnimatedData([]);
      return;
    }
    const full = priceData
      .filter(d => d.sma20 != null)
      .map(d => ({ Date: d.date, Close: +d.close, SMA20: +d.sma20 }));
    let i = 0;
    const run = () => {
      if (i <= full.length) {
        setSmaAnimatedData(full.slice(0, i));
        i++;
        requestAnimationFrame(run);
      }
    };
    run();
  }, [priceData, showSMA, range]);

  // Render candlestick chart
  useEffect(() => {
    if (!showCandles || !chartContainerRef.current) return;
    chartContainerRef.current.innerHTML = "";
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { color: darkMode ? "#121212" : "#ffffff" },
        textColor: darkMode ? "#ffffff" : "#000000",
      },
      grid: {
        vertLines: { color: darkMode ? "#444" : "#eee" },
        horzLines: { color: darkMode ? "#444" : "#eee" },
      },
      width: chartContainerRef.current.clientWidth,
      height: 250,
    });
    const cdata = priceData
      .map(d => ({
        time: Math.floor(new Date(d.date).getTime() / 1000),
        open: +d.open,
        high: +d.high,
        low: +d.low,
        close: +d.close,
      }))
      .filter(d => !isNaN(d.open));
    chart.addCandlestickSeries().setData(cdata);
    chart.timeScale().fitContent();
    Object.entries({ sma20: showSMA, ...showEMAs }).forEach(([key, vis]) => {
      if (!vis) return;
      const series = chart.addLineSeries({ color: emaColorMap[key], lineWidth: 2 });
      const data = priceData
        .filter(x => x[key] != null)
        .map(x => ({ time: Math.floor(new Date(x.date).getTime() / 1000), value: +x[key] }));
      let j = 0;
      const anim = () => {
        if (j <= data.length) {
          series.setData(data.slice(0, j));
          j++;
          requestAnimationFrame(anim);
        }
      };
      anim();
    });
    return () => chart.remove();
  }, [priceData, showCandles, showSMA, showEMAs, darkMode]);

  // Prepare line chart data
  const formatForLineChart = () =>
    priceData.map(d => ({
      Date: d.date,
      Close: parseFloat(d.close),
      SMA20: d.sma20 != null ? parseFloat(d.sma20) : null,
      ema9: d.ema9 != null ? parseFloat(d.ema9) : null,
      ema20: d.ema20 != null ? parseFloat(d.ema20) : null,
      ema50: d.ema50 != null ? parseFloat(d.ema50) : null,
      ema100: d.ema100 != null ? parseFloat(d.ema100) : null,
      ema200: d.ema200 != null ? parseFloat(d.ema200) : null,
    }));

  const lineChartData = showSMA ? smaAnimatedData : formatForLineChart();

  // UI helpers
  const Spinner = () => (
    <div className="flex items-center justify-center mt-6">
      <div className="w-6 h-6 border-4 border-gray-400 border-dashed rounded-full animate-spin" />
    </div>
  );
  const getSignalTextColor = s => (s === "Buy" ? "text-green-500" : "text-red-500");
  const getSignalBarColor = s => (s === "Buy" ? "bg-green-500" : "bg-red-500");
  const rangeOptions = [
    { label: "1M", value: "1mo" },
    { label: "3M", value: "3mo" },
    { label: "6M", value: "6mo" },
    { label: "YTD", value: "ytd" },
    { label: "1Y", value: "1y" },
  ];

  return (
    <div className={`${darkMode ? "bg-[#121212] text-white" : "bg-[#f5f5f5] text-gray-900"} min-h-screen font-sans transition-colors duration-500 ease-in-out`}>
      <header className={`border-b px-8 py-4 flex justify-between items-center shadow-sm transition-colors duration-500 ease-in-out ${darkMode ? "bg-[#1e1e1e]" : "bg-white"}`}>
        <h1 className="text-2xl font-semibold tracking-tight">SignalSense AI</h1>
        <button onClick={() => setDarkMode(!darkMode)} className="px-4 py-2 rounded shadow text-sm font-medium transition bg-gray-700 text-white hover:bg-gray-600 dark:bg-gray-300 dark:text-gray-900 dark:hover:bg-gray-200">
          {darkMode ? "Light Mode" : "Dark Mode"}
        </button>
      </header>

      <main className="p-8 flex flex-col items-center transition-colors duration-500 ease-in-out">
        {/* Input & Button */}
        <div className="flex gap-3 mb-6">
          <input
            className={`px-4 py-2 border rounded-lg shadow-sm focus:outline-none focus:ring-2 w-64 placeholder-gray-400 text-sm transition ${darkMode ? "bg-[#2a2a2a] text-white border-gray-600 focus:ring-gray-500" : "bg-white text-gray-900 border-gray-300 focus:ring-gray-300"}`}
            placeholder="Enter ticker (e.g. AAPL)"
            value={ticker}
            onChange={e => setTicker(e.target.value)}
          />
          <button
            onClick={() => getSignal()}
            disabled={loading}
            className={`px-4 py-2 rounded-lg font-medium text-sm transition ${loading ? "bg-gray-400 text-white" : darkMode ? "bg-gray-100 text-black hover:bg-gray-200" : "bg-gray-900 text-white hover:bg-gray-800"}`}
          >
            {loading ? "Loading..." : "Get Signal"}
          </button>
        </div>

        {loading && <Spinner />}&#10;
                {/* Result Box */}
                {result && (
          <div
            className={`rounded-xl shadow-lg p-6 w-full max-w-xl mb-10 transition-colors duration-500 ease-in-out ${
              darkMode ? "bg-[#1f1f1f]" : "bg-white"
            }`}
          >
            {result.error ? (
              <p className="text-red-500 font-semibold">{result.error}</p>
            ) : (
              <>
                <div className="flex items-baseline justify-between mb-2">
                  <h2 className="text-2xl font-bold">{result.ticker}</h2>
                  <p
                    className={`text-lg font-medium ${getSignalTextColor(
                      result.signal
                    )}`}
                  >
                    {result.signal}
                  </p>
                </div>
                <div className="mb-4">
                  <p className="text-sm text-gray-500 mb-1">Confidence</p>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className={`h-3 rounded-full transition-all duration-700 ease-in-out ${getSignalBarColor(
                        result.signal
                      )} bg-opacity-80`}
                      style={{ width: `${barWidth}%` }}
                    />
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {animatedConfidence}%
                  </p>
                </div>
                <p className="text-sm leading-relaxed text-gray-700 dark:text-gray-300">
                  {result.explanation}
                </p>
              </>
            )}
          </div>
        )}

        {/* Prediction History */}
        {history.length > 0 && (
          <div className="mt-4 w-full max-w-xl">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300">
                Prediction History
              </h3>
              <button
                onClick={() => setHistory([])}
                className="text-sm text-gray-500 hover:text-gray-800 dark:hover:text-white"
              >
                Clear History
              </button>
            </div>
            <ul className="space-y-3">
              {history.map((item, idx) => (
                <li
                  key={idx}
                  className={`p-4 rounded-lg shadow flex justify-between items-center transition-colors duration-500 ease-in-out ${
                    darkMode
                      ? "bg-[#1e1e1e] text-white"
                      : "bg-white text-gray-900"
                  }`}
                >
                  <span className="font-semibold">{item.ticker}</span>
                  <span
                    className={`text-sm font-medium ${getSignalTextColor(
                      item.signal
                    )}`}
                  >
                    {item.signal} ({item.confidence}%)
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Price Chart Controls */}
        <div className="mb-4 w-full max-w-xl flex flex-wrap gap-2 items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300">
            Price Chart ({range})
          </h3>
          <div className="flex flex-wrap gap-2 items-center">
            {rangeOptions.map(opt => (
              <button
                key={opt.value}
                onClick={() => setRange(opt.value)}
                className={`px-2 py-1 text-sm rounded ${
                  range === opt.value
                    ? darkMode
                      ? "bg-gray-100 text-black"
                      : "bg-gray-900 text-white"
                    : darkMode
                    ? "bg-[#2a2a2a] text-white"
                    : "bg-gray-200 text-black"
                }`}
              >
                {opt.label}
              </button>
            ))}
            <label className="flex items-center gap-1">
              <input
                type="checkbox"
                checked={showCandles}
                onChange={() => setShowCandles(!showCandles)}
              />
              Candlesticks
            </label>
            <label className="flex items-center gap-1">
              <input
                type="checkbox"
                checked={showSMA}
                onChange={() => setShowSMA(!showSMA)}
              />
              SMA 20
            </label>
            {Object.entries(showEMAs).map(([key, val]) => (
              <label key={key} className="flex items-center gap-1">
                <input
                  type="checkbox"
                  checked={val}
                  onChange={() =>
                    setShowEMAs(prev => ({ ...prev, [key]: !prev[key] }))
                  }
                />
                {key.toUpperCase()}
              </label>
            ))}
            <label className="flex items-center gap-1">
              <input
                type="checkbox"
                checked={showRSI}
                onChange={() => setShowRSI(!showRSI)}
              />
              RSI
            </label>
          </div>
        </div>

        {/* Chart Display */}
        {histError && (
          <p className="text-red-500 mb-4">History error: {histError}</p>
        )}
        {priceData.length > 0 && (
          <div className="mb-12 w-full max-w-xl">
            {showCandles ? (
              <div
                ref={chartContainerRef}
                className="w-full"
                style={{ height: 250 }}
              />
            ) : (
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={lineChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="Date" tick={{ fontSize: 10 }} />
                  <YAxis domain={["auto", "auto"]} tick={{ fontSize: 10 }} />
                  <Tooltip />
                  <Line
                    type="monotone"
                    dataKey="Close"
                    stroke={darkMode ? "#90cdf4" : "#1a202c"}
                    strokeWidth={2}
                    isAnimationActive={false}
                  />
                  {showSMA && (
                    <Line
                      type="monotone"
                      dataKey="SMA20"
                      stroke="#eab308"
                      strokeWidth={2}
                      dot={false}
                      isAnimationActive={false}
                    />
                  )}
                  {Object.entries(showEMAs).map(
                    ([key, isVisible]) =>
                      isVisible && (
                        <Line
                          key={key}
                          type="monotone"
                          dataKey={key}
                          stroke={emaColorMap[key]}
                          strokeWidth={2}
                          dot={false}
                          isAnimationActive={false}
                        />
                      )
                  )}
                </LineChart>
              </ResponsiveContainer>
            )}
            {showRSI && (
              <div className="mt-6 w-full max-w-xl">
                <h4 className="text-sm font-semibold mb-2 text-gray-600 dark:text-gray-300">
                  Relative Strength Index (RSI)
                </h4>
                <ResponsiveContainer width="100%" height={100}>
                  <LineChart
                    data={priceData.map(d => ({
                      Date: d.date,
                      RSI: d.rsi != null ? parseFloat(d.rsi) : null
                    }))}
                  >
                    <XAxis dataKey="Date" hide />
                    <YAxis domain={[0, 100]} ticks={[30, 50, 70]} />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="RSI"
                      stroke="#f97316"
                      strokeWidth={2}
                      dot={false}
                      isAnimationActive={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

