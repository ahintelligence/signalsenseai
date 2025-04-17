// src/App.jsx
import React, { useState, useEffect, useRef } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { createChart } from "lightweight-charts";

import HelpTooltip from "./components/HelpTooltip";
import TooltipWord from "./components/TooltipWord";
import GlossaryModal from "./components/GlossaryModal";

// LocalStorage helpers
const getStored = (key, fallback) => {
  try {
    const v = localStorage.getItem(key);
    return v ? JSON.parse(v) : fallback;
  } catch {
    return fallback;
  }
};
const setStored = (key, val) => {
  try {
    localStorage.setItem(key, JSON.stringify(val));
  } catch {}
};

// EMA color map & glossary
const emaColorMap = {
  ema9: "#b15928",
  ema20: "#6b7280",
  ema50: "#4b5563",
  ema100: "#374151",
  ema200: "#111827",
};
const glossary = {
  SMA20:
    "Simple Moving Average over 20 days. Smooths out short-term price noise.",
  EMA: "Exponential Moving Average. Gives more weight to recent price data.",
  RSI:
    "Relative Strength Index. Identifies overbought (70+) or oversold (30-) conditions.",
  Candlesticks:
    "Displays daily open, high, low, and close prices as visual bars.",
  Confidence:
    "How confident the AI model is in its prediction. Higher % = stronger signal.",
};

export default function App() {
  // 1️⃣ Toggles
  const [darkMode, setDarkMode] = useState(() => getStored("darkMode", false));
  const [showCandles, setShowCandles] = useState(() =>
    getStored("showCandles", false)
  );
  const [showSMA, setShowSMA] = useState(() => getStored("showSMA", true));
  const [showRSI, setShowRSI] = useState(() => getStored("showRSI", false));
  const [showEMAs, setShowEMAs] = useState(() =>
    getStored("showEMAs", {
      ema9: false,
      ema20: false,
      ema50: false,
      ema100: false,
      ema200: false,
    })
  );
  useEffect(() => setStored("darkMode", darkMode), [darkMode]);
  useEffect(() => setStored("showCandles", showCandles), [showCandles]);
  useEffect(() => setStored("showSMA", showSMA), [showSMA]);
  useEffect(() => setStored("showRSI", showRSI), [showRSI]);
  useEffect(() => setStored("showEMAs", showEMAs), [showEMAs]);

  // 2️⃣ Glossary modal
  const [glossaryOpen, setGlossaryOpen] = useState(false);

  // 3️⃣ Core state & refs
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

  const chartRef = useRef(null);
  const prevTicker = useRef("");

  // 4️⃣ Fetch prediction & history via Vite proxy
  const getSignal = async (symbol = ticker) => {
    if (!symbol) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch(`/predict/${symbol.toUpperCase()}`);
      const data = await res.json();
      setResult(data);
      if (!data.error) setHistory((prev) => [...prev, data]);
      await fetchHistory(symbol, range);
    } catch {
      setResult({ error: "Failed to fetch signal." });
    } finally {
      setLoading(false);
    }
  };
  const fetchHistory = async (symbol, selectedRange) => {
    try {
      const res = await fetch(
        `/history/${symbol.toUpperCase()}?range=${selectedRange}`
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

  // 5️⃣ Animate confidence bar
  useEffect(() => {
    if (result && !result.error && result.ticker !== prevTicker.current) {
      setBarWidth(0);
      requestAnimationFrame(() =>
        requestAnimationFrame(() => setBarWidth(result.confidence))
      );
      let start = 0,
        end = result.confidence,
        steps = Math.ceil(900 / 25),
        inc = end / steps;
      const timer = setInterval(() => {
        start += inc;
        setAnimatedConfidence(Math.min(end, Math.round(start)));
        if (start >= end) clearInterval(timer);
      }, 25);
      prevTicker.current = result.ticker;
      return () => clearInterval(timer);
    }
  }, [result]);

  // 6️⃣ Refetch history on range change
  useEffect(() => {
    if (ticker) fetchHistory(ticker, range);
  }, [range]);

  // 7️⃣ Animate SMA path
  useEffect(() => {
    if (!showSMA || !priceData.length) {
      setSmaAnimatedData([]);
      return;
    }
    const full = priceData
      .filter((d) => d.sma20 != null)
      .map((d) => ({ Date: d.date, Close: +d.close, SMA20: +d.sma20 }));
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

  // 8️⃣ Draw candlesticks + overlays
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
    });

    const cdata = priceData
      .map((d) => ({
        time: Math.floor(new Date(d.date).getTime() / 1000),
        open: +d.open,
        high: +d.high,
        low: +d.low,
        close: +d.close,
      }))
      .filter((d) => !isNaN(d.open));
    chart.addCandlestickSeries().setData(cdata);
    chart.timeScale().fitContent();

    Object.entries({ sma20: showSMA, ...showEMAs }).forEach(
      ([key, visible]) => {
        if (!visible) return;
        const series = chart.addLineSeries({
          color: emaColorMap[key],
          lineWidth: 2,
        });
        const data = priceData
          .filter((x) => x[key] != null)
          .map((x) => ({
            time: Math.floor(new Date(x.date).getTime() / 1000),
            value: +x[key],
          }));
        let j = 0;
        const animate = () => {
          if (j <= data.length) {
            series.setData(data.slice(0, j));
            j++;
            requestAnimationFrame(animate);
          }
        };
        animate();
      }
    );

    return () => chart.remove();
  }, [priceData, showCandles, showSMA, showEMAs, darkMode]);

  // 9️⃣ Data prep & UI helpers
  const formatForLineChart = () =>
    priceData.map((d) => ({
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
  const Spinner = () => (
    <div className="flex items-center justify-center mt-6">
      <div className="w-6 h-6 border-4 border-gray-500 border-dashed rounded-full animate-spin" />
    </div>
  );
  const getSignalTextColor = (s) =>
    s === "Buy" ? "text-green-400" : "text-red-400";
  const getSignalBarColor = (s) =>
    s === "Buy" ? "bg-green-400" : "bg-red-400";
  const rangeOptions = [
    { label: "1M", value: "1mo" },
    { label: "3M", value: "3mo" },
    { label: "6M", value: "6mo" },
    { label: "YTD", value: "ytd" },
    { label: "1Y", value: "1y" },
  ];

  // 🔟 JSX
  return (
    <div
      className={`min-h-screen relative ${
        darkMode ? "bg-gray-950 text-gray-100" : "bg-gray-100 text-gray-900"
      } transition-colors duration-500`}
    >
      {/* Glossary */}
      <button
        onClick={() => setGlossaryOpen(true)}
        className="fixed bottom-4 right-4 bg-gray-700 text-gray-100 p-2 rounded-full shadow hover:bg-gray-600 transition"
      >
        ?
      </button>
      <GlossaryModal
        open={glossaryOpen}
        onClose={() => setGlossaryOpen(false)}
        glossary={glossary}
        darkMode={darkMode}
      />

      <header
        className={`border-b px-8 py-4 flex justify-between items-center shadow-sm ${
          darkMode ? "bg-gray-900" : "bg-gray-200"
        } transition-colors duration-500`}
      >
        <h1 className="text-2xl font-semibold tracking-tight">
          SignalSense AI
        </h1>
        <button
          onClick={() => setDarkMode(!darkMode)}
          className="px-4 py-2 rounded shadow text-sm font-medium transition bg-gray-700 text-gray-100 hover:bg-gray-600"
        >
          {darkMode ? "Light Mode" : "Dark Mode"}
        </button>
      </header>

      <main className="p-8 flex flex-col items-center">
        {/* Input row */}
        <div className="flex gap-3 mb-6 w-full max-w-xl">
          <input
            className={`flex-1 px-4 py-2 border rounded-lg shadow-sm focus:outline-none focus:ring-2 placeholder-gray-400 text-sm transition ${
              darkMode
                ? "bg-gray-800 text-gray-100 border-gray-600 focus:ring-gray-500"
                : "bg-white text-gray-900 border-gray-300 focus:ring-gray-300"
            }`}
            placeholder="Enter ticker (e.g. AAPL)"
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
          />
          <button
            onClick={() => getSignal()}
            disabled={loading}
            className={`px-4 py-2 rounded-lg font-medium text-sm transition ${
              loading
                ? "bg-gray-500 text-gray-100 cursor-not-allowed"
                : darkMode
                ? "bg-gray-700 text-gray-100 hover:bg-gray-600"
                : "bg-gray-900 text-gray-100 hover:bg-gray-800"
            }`}
          >
            {loading ? "Loading..." : "Get Signal"}
          </button>
        </div>
        {loading && <Spinner />}

        {/* Signal result */}
        {result && (
          <div
            className={`rounded-xl shadow-lg p-6 w-full max-w-xl mb-10 transition-colors duration-500 ${
              darkMode ? "bg-gray-900" : "bg-white"
            }`}
          >
            {result.error ? (
              <p className="text-red-400 font-semibold">{result.error}</p>
            ) : (
              <>
                <div className="flex justify-between items-baseline mb-2">
                  <h2 className="text-2xl font-bold">{result.ticker}</h2>
                  <p
                    className={`text-lg font-medium ${getSignalTextColor(
                      result.signal
                    )}`}
                  >
                    {result.signal}
                  </p>
                </div>

                {/* Confidence bar */}
                <div className="mb-4">
                  <p className="text-sm text-gray-400 mb-1 flex items-center">
                    Confidence
                    <HelpTooltip text={glossary.Confidence} />
                  </p>
                  <div className="w-full bg-gray-800 rounded-full h-3">
                    <div
                      className={`h-3 rounded-full transition-all duration-700 ease-in-out ${getSignalBarColor(
                        result.signal
                      )}`}
                      style={{ width: `${barWidth}%` }}
                    />
                  </div>
                  <p className="text-xs text-gray-400 mt-1">
                    {animatedConfidence}%
                  </p>
                </div>

                {/* Explanation with glossary */}
                <p className="text-sm leading-relaxed mb-2">
                  {result.explanation.split(/\s+/).map((w, i) =>
                    glossary[w.toUpperCase()] ? (
                      <TooltipWord
                        key={i}
                        word={w}
                        description={glossary[w.toUpperCase()]}
                      />
                    ) : (
                      w + " "
                    )
                  )}
                </p>

                {/* Inline hints */}
                {result.signal === "Buy" && (
                  <p className="text-xs text-green-400 mt-2">
                    Indicates a likely price increase.
                  </p>
                )}
                {result.signal === "Sell" && (
                  <p className="text-xs text-red-400 mt-2">
                    Indicates a potential price decline.
                  </p>
                )}
              </>
            )}
          </div>
        )}

        {/* History */}
        {history.length > 0 && (
          <div className="w-full max-w-xl mb-8">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Prediction History</h3>
              <button
                onClick={() => setHistory([])}
                className="text-sm text-gray-500 hover:text-gray-700 transition"
              >
                Clear
              </button>
            </div>
            <ul className="space-y-3">
              {history.map((item, i) => (
                <li
                  key={i}
                  className={`p-4 rounded-lg shadow flex justify-between items-center ${
                    darkMode ? "bg-gray-800" : "bg-white"
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

        {/* Chart controls */}
        <div className="w-full max-w-xl mb-6 flex flex-wrap gap-4 items-center">
          <h3 className="text-lg font-semibold">Price Chart ({range})</h3>
          {rangeOptions.map((opt) => (
            <button
              key={opt.value}
              onClick={() => setRange(opt.value)}
              className={`px-3 py-1 rounded text-sm transition ${
                range === opt.value
                  ? darkMode
                    ? "bg-gray-700 text-gray-100"
                    : "bg-gray-900 text-gray-100"
                  : darkMode
                  ? "bg-gray-800 text-gray-300"
                  : "bg-gray-200 text-gray-700"
              }`}
            >
              {opt.label}
            </button>
          ))}
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={showCandles}
              onChange={() => setShowCandles(!showCandles)}
            />
            Candlesticks <HelpTooltip text={glossary.Candlesticks} />
          </label>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={showSMA}
              onChange={() => setShowSMA(!showSMA)}
            />
            SMA 20 <HelpTooltip text={glossary.SMA20} />
          </label>
          {Object.keys(showEMAs).map((k) => (
            <label key={k} className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={showEMAs[k]}
                onChange={() =>
                  setShowEMAs((prev) => ({ ...prev, [k]: !prev[k] }))
                }
              />
              {k.toUpperCase()} <HelpTooltip text={glossary.EMA} />
            </label>
          ))}
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={showRSI}
              onChange={() => setShowRSI(!showRSI)}
            />
            RSI <HelpTooltip text={glossary.RSI} />
          </label>
        </div>

        {/* Chart display */}
        {histError && <p className="text-red-400 mb-4">Error: {histError}</p>}
        {priceData.length > 0 && (
          <div className="w-full max-w-xl">
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
                    isAnimationActive={false}
                  />
                  {showSMA && (
                    <Line
                      type="monotone"
                      dataKey="SMA20"
                      stroke="#9ca3af"
                      strokeWidth={2}
                      dot={false}
                      isAnimationActive={false}
                    />
                  )}
                  {Object.entries(showEMAs).map(
                    ([k, v]) =>
                      v && (
                        <Line
                          key={k}
                          type="monotone"
                          dataKey={k}
                          stroke={emaColorMap[k]}
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
                <h4 className="text-sm font-semibold mb-2 text-gray-400">
                  RSI
                </h4>
                <ResponsiveContainer width="100%" height={100}>
                  <LineChart
                    data={priceData.map((d) => ({
                      Date: d.date,
                      RSI: d.rsi != null ? parseFloat(d.rsi) : null,
                    }))}
                  >
                    <XAxis dataKey="Date" hide />
                    <YAxis domain={[0, 100]} ticks={[30, 50, 70]} />
                    <RechartsTooltip />
                    <Line
                      type="monotone"
                      dataKey="RSI"
                      stroke="#9ca3af"
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


