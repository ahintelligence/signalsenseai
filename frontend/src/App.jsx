import React, { useState, useEffect, useRef } from "react";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from "recharts";
import { createChart } from "lightweight-charts";

function App() {
  const [ticker, setTicker] = useState("");
  const [range, setRange] = useState("1mo");
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [priceData, setPriceData] = useState([]);
  const [barWidth, setBarWidth] = useState(0);
  const [animatedConfidence, setAnimatedConfidence] = useState(0);
  const [loading, setLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [showCandles, setShowCandles] = useState(false);
  const chartContainerRef = useRef(null);
  const chartInstanceRef = useRef(null);
  const prevTicker = useRef("");

  const getSignal = async (symbol = ticker) => {
    if (!symbol) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch(`http://localhost:8000/predict/${symbol.toUpperCase()}`);
      const data = await res.json();
      setResult(data);
      if (!data.error) {
        setHistory(prev => [...prev, data]);
      }
      await fetchHistory(symbol, range);
    } catch (err) {
      setResult({ error: "Failed to fetch signal. Check server or ticker symbol." });
    } finally {
      setLoading(false);
    }
  };

  const fetchHistory = async (symbol, selectedRange) => {
    try {
      const histRes = await fetch(`http://localhost:8000/history/${symbol.toUpperCase()}?range=${selectedRange}`);
      const histData = await histRes.json();
      setPriceData(histData.history || []);
    } catch (err) {
      console.error("Failed to fetch history:", err);
    }
  };

  useEffect(() => {
    if (result && !result.error && result.ticker !== prevTicker.current) {
      setBarWidth(0);
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          setBarWidth(result.confidence);
        });
      });

      let start = 0;
      const end = result.confidence;
      const duration = 900;
      const stepTime = 25;
      const steps = Math.ceil(duration / stepTime);
      const increment = end / steps;

      const timer = setInterval(() => {
        start += increment;
        if (start >= end) {
          setAnimatedConfidence(end);
          clearInterval(timer);
        } else {
          setAnimatedConfidence(Math.round(start));
        }
      }, stepTime);

      prevTicker.current = result.ticker;
      return () => clearInterval(timer);
    }
  }, [result]);

  useEffect(() => {
    if (ticker) {
      fetchHistory(ticker, range);
    }
  }, [range]);

  useEffect(() => {
    if (showCandles && chartContainerRef.current && priceData.length > 0) {
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
      const candleSeries = chart.addCandlestickSeries();
      candleSeries.setData(formatForCandles());
      chartInstanceRef.current = chart;
    }
  }, [showCandles, priceData, darkMode]);

  const getSignalTextColor = (signal) => {
    if (!signal) return "text-gray-500";
    return signal === "Buy" ? "text-green-500" : "text-red-500";
  };

  const getSignalBarColor = (signal) => {
    if (!signal) return "bg-gray-400";
    return signal === "Buy" ? "bg-green-500" : "bg-red-500";
  };

  const Spinner = () => (
    <div className="flex items-center justify-center mt-6">
      <div className="w-6 h-6 border-4 border-gray-400 border-dashed rounded-full animate-spin"></div>
    </div>
  );

  const rangeOptions = [
    { label: "1M", value: "1mo" },
    { label: "3M", value: "3mo" },
    { label: "6M", value: "6mo" },
    { label: "YTD", value: "ytd" },
    { label: "1Y", value: "1y" },
  ];

  const formatForCandles = () => {
    return priceData.map(d => ({
      time: d.Date,
      open: d.Open,
      high: d.High,
      low: d.Low,
      close: d.Close
    }));
  };


  return (
    <div className={`${darkMode ? "bg-[#121212] text-white" : "bg-[#f5f5f5] text-gray-900"} min-h-screen font-sans transition-colors duration-500 ease-in-out`}>
      <header className={`border-b px-8 py-4 flex justify-between items-center shadow-sm transition-colors duration-500 ease-in-out ${darkMode ? "bg-[#1e1e1e]" : "bg-white"}`}>
        <h1 className="text-2xl font-semibold tracking-tight transition-colors duration-300">SignalSense AI</h1>
        <button
          onClick={() => setDarkMode(!darkMode)}
          className="px-4 py-2 rounded shadow text-sm font-medium transition bg-gray-700 text-white hover:bg-gray-600 dark:bg-gray-300 dark:text-gray-900 dark:hover:bg-gray-200"
        >
          {darkMode ? "Light Mode" : "Dark Mode"}
        </button>
      </header>

      <main className="p-8 flex flex-col items-center transition-colors duration-500 ease-in-out">
        <div className="flex gap-3 mb-6">
          <input
            className={`px-4 py-2 border rounded-lg shadow-sm focus:outline-none focus:ring-2 w-64 placeholder-gray-400 text-sm transition ${darkMode ? "bg-[#2a2a2a] text-white border-gray-600 focus:ring-gray-500" : "bg-white text-gray-900 border-gray-300 focus:ring-gray-300"}`}
            placeholder="Enter ticker (e.g. AAPL)"
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
          />
          <button
            className={`px-4 py-2 rounded-lg font-medium text-sm transition ${loading ? "bg-gray-400 text-white" : darkMode ? "bg-gray-100 text-black hover:bg-gray-200" : "bg-gray-900 text-white hover:bg-gray-800"}`}
            onClick={() => getSignal()}
            disabled={loading}
          >
            {loading ? "Loading..." : "Get Signal"}
          </button>
        </div>

        {loading && <Spinner />}

        {result && (
          <div className={`rounded-xl shadow-lg p-6 w-full max-w-xl animate-fadeIn mb-10 transition-colors duration-500 ease-in-out ${darkMode ? 'bg-[#1f1f1f]' : 'bg-white'}`}>
            {result.error ? (
              <p className="text-red-500 font-semibold">{result.error}</p>
            ) : (
              <>
                <div className="flex items-baseline justify-between mb-2">
                  <h2 className="text-2xl font-bold">{result.ticker}</h2>
                  <p className={`text-lg font-medium ${getSignalTextColor(result.signal)}`}>{result.signal}</p>
                </div>
                <div className="mb-4">
                  <p className="text-sm text-gray-500 mb-1">Confidence</p>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div className={`h-3 rounded-full transition-all duration-700 ease-in-out ${getSignalBarColor(result.signal)} bg-opacity-80`} style={{ width: `${barWidth}%` }}></div>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">{animatedConfidence}%</p>
                </div>
                <p className="text-sm leading-relaxed text-gray-700 dark:text-gray-300">{result.explanation}</p>
              </>
            )}
          </div>
        )}

        {priceData.length > 0 && (
          <div className="mb-12 w-full max-w-xl">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300">Price Chart ({range})</h3>
              <div className="flex flex-wrap gap-2 items-center">
                {rangeOptions.map(opt => (
                  <button
                    key={opt.value}
                    onClick={() => setRange(opt.value)}
                    className={`px-2 py-1 text-sm rounded ${range === opt.value ? (darkMode ? "bg-gray-100 text-black" : "bg-gray-900 text-white") : (darkMode ? "bg-[#2a2a2a] text-white" : "bg-gray-200 text-black")}`}
                  >
                    {opt.label}
                  </button>
                ))}
                <label className="ml-4 text-sm flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={showCandles}
                    onChange={() => setShowCandles(!showCandles)}
                  />
                  Candlesticks
                </label>
              </div>
            </div>

            {showCandles ? (
              <div ref={chartContainerRef} className="w-full" style={{ height: "250px" }} />
            ) : (
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={priceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="Date" tick={{ fontSize: 10 }} />
                  <YAxis domain={['auto', 'auto']} tick={{ fontSize: 10 }} />
                  <Tooltip />
                  <Line type="monotone" dataKey="Close" stroke={darkMode ? "#90cdf4" : "#1a202c"} strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;








