import React, { useState, useEffect, useRef, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import './styles/vantheon-enhanced.css';
import Header from "./components/Header";
import SearchBar from "./components/SearchBar";
import GlossaryModal from "./components/GlossaryModal";
import SignalSummary from "./components/SignalSummary";
import PredictionHistory from "./components/PredictionHistory";
import ChartDisplay from "./components/ChartDisplay";
import Spinner from "./components/Spinner";
import ErrorNotification from "./components/ErrorNotification";
import { getStored, setStored } from "./utils/localStorage";
import { useSignalLogic } from "./hooks/useSignalLogic";

function flipA(text) {
  return text.replace(/A/g, "Ʌ");
}

export default function App() {
  const [darkMode, setDarkMode] = useState(() => getStored("darkMode", false));
  const [glossaryOpen, setGlossaryOpen] = useState(false);
  const [showSplash, setShowSplash] = useState(true);
  const [hasClickedGetSignal, setHasClickedGetSignal] = useState(false);
  const [latestPrice, setLatestPrice] = useState(null);
  const [lockedTicker, setLockedTicker] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  const [showSMA, setShowSMA] = useState(() => getStored("showSMA", true));
  const [showRSI, setShowRSI] = useState(() => getStored("showRSI", false));
  const [showEMAs, setShowEMAs] = useState(() =>
    getStored("showEMAs", { ema9: false, ema20: false, ema50: false, ema100: false, ema200: false })
  );
  const [enlarged, setEnlarged] = useState(false);

  // Glossary definitions for the modal
  const glossary = {
    SMA20: "Simple Moving Average calculated over 20 days.",
    EMA9: "Exponential Moving Average with a 9-day span.",
    EMA20: "Exponential Moving Average with a 20-day span.",
    EMA50: "Exponential Moving Average with a 50-day span.",
    EMA100: "Exponential Moving Average with a 100-day span.",
    EMA200: "Exponential Moving Average with a 200-day span.",
    RSI: "Relative Strength Index measures momentum on a scale of 0 to 100.",
    Candlesticks: "Chart type showing open, high, low, and close prices.",
    Confidence: "Model confidence level in the signal, shown as a percentage.",
  };

  const {
    ticker,
    setTicker,
    range,
    setRange,
    result,
    setResult,
    history,
    setHistory,
    priceData,
    barWidth,
    animatedConfidence,
    loading,
    getSignal: originalGetSignal,
    histError,
  } = useSignalLogic();

  const chartRef = useRef(null);

  // Splash fade-out
  useEffect(() => {
    const timer = setTimeout(() => setShowSplash(false), 3500);
    return () => clearTimeout(timer);
  }, []);

  // Persist user preferences
  useEffect(() => setStored("darkMode", darkMode), [darkMode]);
  useEffect(() => setStored("showSMA", showSMA), [showSMA]);
  useEffect(() => setStored("showRSI", showRSI), [showRSI]);
  useEffect(() => setStored("showEMAs", showEMAs), [showEMAs]);

  // Poll latest price every 5 minutes
  useEffect(() => {
    if (!lockedTicker) return;
    const fetchLatestPrice = async () => {
      try {
        const res = await fetch(`http://localhost:8000/latest-price/${lockedTicker}`);
        const data = await res.json();
        setLatestPrice(data);
      } catch (err) {
        console.error("Failed to refresh latest price:", err);
      }
    };
    fetchLatestPrice();
    const interval = setInterval(fetchLatestPrice, 300000);
    return () => clearInterval(interval);
  }, [lockedTicker]);

  const handleSignalFetch = async () => {
    const res = await originalGetSignal();
    if (res?.error) {
      setErrorMessage(res.error);
      return;
    }
    setLockedTicker(ticker);
    setHasClickedGetSignal(true);
  };

  const handleTickerChange = (val) => {
    setTicker(val);
    if (result?.error) setResult(null);
  };

  // Prepare data arrays for ChartDisplay
  const candleData = useMemo(
    () =>
      priceData.map((d) => ({
        time: Math.floor(new Date(d.date).getTime() / 1000),
        open: d.open,
        high: d.high,
        low: d.low,
        close: d.close,
      })),
    [priceData]
  );

  const smaData = useMemo(
    () =>
      priceData
        .filter((d) => d.sma20 != null)
        .map((d) => ({
          time: Math.floor(new Date(d.date).getTime() / 1000),
          value: d.sma20,
        })),
    [priceData]
  );

  const emaSeries = useMemo(
    () =>
      Object.entries(showEMAs).map(([key, v]) => ({
        key,
        data: v
          ? priceData
              .filter((d) => d[key] != null)
              .map((d) => ({
                time: Math.floor(new Date(d.date).getTime() / 1000),
                value: d[key],
              }))
          : [],
      })),
    [priceData, showEMAs]
  );

  const rsiData = useMemo(
    () =>
      priceData
        .filter((d) => d.rsi != null)
        .map((d) => ({
          time: Math.floor(new Date(d.date).getTime() / 1000),
          value: d.rsi,
        })),
    [priceData]
  );

  return (
    <div
      className={`min-h-screen font-['Exo 2'],sans-serif ${
        darkMode ? "bg-black text-zinc-200" : "bg-zinc-100 text-zinc-900"
      } transition-colors duration-500`}
    >
      {/* Splash Screen */}
      <AnimatePresence>
        {showSplash && (
          <motion.div
            key="splash"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 1.5 }}
            className="fixed inset-0 bg-black text-white flex items-center justify-center z-50"
          >
            <h1 className="text-3xl font-bold tracking-wider animate-fadeInSlow">
              Welcome to Lattice by Vantheon
            </h1>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error Notification & Glossary */}
      {errorMessage && (
        <ErrorNotification
          message={errorMessage}
          onClose={() => setErrorMessage(null)}
          darkMode={darkMode}
        />
      )}
      <GlossaryModal
        open={glossaryOpen}
        onClose={() => setGlossaryOpen(false)}
        darkMode={darkMode}
        glossary={glossary}
      />

      {/* Header */}
      <Header
        darkMode={darkMode}
        toggleDarkMode={() => setDarkMode((p) => !p)}
        onOpenGlossary={() => setGlossaryOpen(true)}
      />

      <main className="px-6 md:px-10 lg:px-16 py-6 max-w-screen-2xl mx-auto">
        {/* Welcome Section */}
        {!hasClickedGetSignal && (
          <motion.div
            key="welcome"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            transition={{ duration: 1 }}
            className="text-center mb-8 animate-fadeInSlow"
          >
            <h2 className="text-2xl font-semibold text-zinc-800 dark:text-zinc-200">
              Welcome to Lattice by Vantheon
            </h2>
            <p className="text-lg text-zinc-500 dark:text-zinc-400 mt-4">
              Enter a stock symbol above to get predictions, view historical data,
              and analyze trends in real-time.
            </p>
            <div className="mt-6 text-zinc-500 dark:text-zinc-300">
              <p className="text-center">Try these example tickers:</p>
              <div className="flex justify-center gap-8 mt-4">
                <span className="text-emerald-400">AAPL</span>
                <span className="text-emerald-400">GOOG</span>
                <span className="text-emerald-400">TSLA</span>
              </div>
            </div>
          </motion.div>
        )}

        {/* Search & Spinner */}
        <SearchBar
          ticker={ticker}
          setTicker={handleTickerChange}
          loading={loading}
          getSignal={handleSignalFetch}
          darkMode={darkMode}
        />
        {loading && <Spinner />}

        {/* Main Content */}
        {hasClickedGetSignal && (
          <motion.div
            key="content"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            transition={{ duration: 1 }}
          >
            {/* Latest Price */}
            <div className="clip-trapezoid data-overlay font-mono text-sm my-6">
              {latestPrice?.close != null ? (
                <p>
                  Latest Price for <strong>{lockedTicker.toUpperCase()}</strong>:{" "}
                  <span className="text-emerald-400">
                    ${Number(latestPrice.close).toFixed(2)}
                  </span>{" "}
                  <span className="text-xs text-zinc-400">
                    ({new Date(latestPrice.date).toLocaleTimeString()})
                  </span>
                </p>
              ) : (
                <p className="text-yellow-400">
                  Could not retrieve latest price for{" "}
                  <strong>{lockedTicker.toUpperCase()}</strong>.
                </p>
              )}
            </div>

            {/* Prediction & History */}
            <div className="flex flex-col lg:flex-row gap-6 w-full animate-fadeInSlow mb-8">
              <div className="lg:w-2/3 w-full">
                <SignalSummary
                  result={result}
                  animatedConfidence={animatedConfidence}
                  barWidth={barWidth}
                  darkMode={darkMode}
                />
              </div>
              <div className="lg:w-1/3 w-full">
                <PredictionHistory
                  history={history}
                  setHistory={setHistory}
                  darkMode={darkMode}
                />
              </div>
            </div>

            {/* Chart & Controls */}
            <div className="flex flex-col lg:flex-row gap-6 w-full animate-fadeInSlow">
              <div
                className="lg:w-2/3 w-full"
                style={{ height: enlarged ? "600px" : "300px" }}
              >
                <ChartDisplay
                  chartRef={chartRef}
                  candleData={candleData}
                  smaData={smaData}
                  emaSeries={emaSeries}
                  rsiData={rsiData}
                  showSMA={showSMA}
                  showRSI={showRSI}
                  enlarged={enlarged}
                  darkMode={darkMode}
                  histError={histError}
                />
              </div>
              <div className="lg:w-1/3 w-full flex flex-col gap-4">
                <div>
                  <label className="block mb-1 text-xs uppercase tracking-wider text-zinc-500">
                    Time Range
                  </label>
                  <select
                    value={range}
                    onChange={(e) => setRange(e.target.value)}
                    className={`w-full p-2 text-sm outline-none transition ${
                      darkMode
                        ? "bg-zinc-800 text-zinc-200 border border-zinc-600"
                        : "bg-white text-zinc-800 border border-zinc-300"
                    }`}
                  >
                    <option value="1mo">1M</option>
                    <option value="3mo">3M</option>
                    <option value="6mo">6M</option>
                    <option value="ytd">YTD</option>
                    <option value="1y">1Y</option>
                  </select>
                </div>
                <div
                  className="border border-dotted p-4 text-sm font-mono uppercase grid grid-cols-2 gap-3"
                  style={{ borderColor: darkMode ? "#52525b" : "#d4d4d8" }}
                >
                  <button
                    onClick={() => setShowSMA((s) => !s)}
                    className={`text-left px-3 py-1 border-dotted transition-all duration-300 ${
                      showSMA ? "text-green-400 border-green-400" : "text-zinc-400 border-zinc-600"
                    } hover:text-white hover:border-white`}
                  >
                    SMA 20
                  </button>
                  <button
                    onClick={() => setShowRSI((r) => !r)}
                    className={`text-left px-3 py-1 border-dotted transition-all duration-300 ${
                      showRSI ? "text-green-400 border-green-400" : "text-zinc-400 border-zinc-600"
                    } hover:text-white hover:border-white`}
                  >
                    RSI
                  </button>
                  {Object.entries(showEMAs).map(([k, v]) => (
                    <button
                      key={k}
                      onClick={() => setShowEMAs((prev) => ({ ...prev, [k]: !prev[k] }))}
                      className={`text-left px-3 py-1 border-dotted transition-all duration-300 ${
                        v ? "text-green-400 border-green-400" : "text-zinc-400 border-zinc-600"
                      } hover:text-white hover:border-white`}
                    >
                      {k.toUpperCase()}
                    </button>
                  ))}
                  <button
                    onClick={() => setEnlarged((e) => !e)}
                    className="col-span-2 px-3 py-1 border-dotted border transition-all duration-300 hover:bg-zinc-700 hover:text-white"
                  >
                    {enlarged ? "Shrink Chart" : "Enlarge Chart"}
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </main>
    </div>
  );
}
















































