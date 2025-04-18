import React, { useState, useEffect, useRef } from "react";
import Header from "./components/Header";
import SearchBar from "./components/SearchBar";
import GlossaryModal from "./components/GlossaryModal";
import SignalSummary from "./components/SignalSummary";
import PredictionHistory from "./components/PredictionHistory";
import LatticeControls from "./components/LatticeControls";
import ChartDisplay from "./components/ChartDisplay";
import InterfaceSection from "./components/InterfaceSection";
import Spinner from "./components/Spinner";

import { getStored, setStored } from "./utils/localStorage";
import { useSignalLogic } from "./hooks/useSignalLogic";
import { useChartAnimation } from "./hooks/useChartAnimation";

function flipA(text) {
  return text.replace(/A/g, 'Ʌ');
}

export default function App() {
  const [darkMode, setDarkMode] = useState(() => getStored("darkMode", false));
  const [glossaryOpen, setGlossaryOpen] = useState(false);
  const [showCandles, setShowCandles] = useState(() => getStored("showCandles", false));
  const [showSMA, setShowSMA] = useState(() => getStored("showSMA", true));
  const [showRSI, setShowRSI] = useState(() => getStored("showRSI", false));
  const [showEMAs, setShowEMAs] = useState(() =>
    getStored("showEMAs", { ema9: false, ema20: false, ema50: false, ema100: false, ema200: false })
  );
  const [showSplash, setShowSplash] = useState(true);
  const [splashClass, setSplashClass] = useState("opacity-0");

  useEffect(() => {
    const fadeIn = setTimeout(() => setSplashClass("opacity-100"), 100);
    const fadeOut = setTimeout(() => setSplashClass("opacity-0"), 2500);
    const hideSplash = setTimeout(() => setShowSplash(false), 3600);
    return () => {
      clearTimeout(fadeIn);
      clearTimeout(fadeOut);
      clearTimeout(hideSplash);
    };
  }, []);

  useEffect(() => setStored("darkMode", darkMode), [darkMode]);
  useEffect(() => setStored("showCandles", showCandles), [showCandles]);
  useEffect(() => setStored("showSMA", showSMA), [showSMA]);
  useEffect(() => setStored("showRSI", showRSI), [showRSI]);
  useEffect(() => setStored("showEMAs", showEMAs), [showEMAs]);

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
    setPriceData,
    barWidth,
    animatedConfidence,
    loading,
    getSignal,
    histError,
  } = useSignalLogic();

  const chartRef = useRef(null);
  const smaAnimatedData = useChartAnimation(priceData, showSMA, range);

  const lineChartData = showSMA
    ? smaAnimatedData
    : priceData.map((d) => ({
        Date: d.date,
        Close: parseFloat(d.close),
        SMA20: d.sma20 != null ? parseFloat(d.sma20) : null,
        ema9: d.ema9 != null ? parseFloat(d.ema9) : null,
        ema20: d.ema20 != null ? parseFloat(d.ema20) : null,
        ema50: d.ema50 != null ? parseFloat(d.ema50) : null,
        ema100: d.ema100 != null ? parseFloat(d.ema100) : null,
        ema200: d.ema200 != null ? parseFloat(d.ema200) : null,
      }));

  const glossary = {
    SMA20: "Simple Moving Average over 20 days.",
    EMA: "Exponential Moving Average. More weight to recent prices.",
    RSI: "Relative Strength Index. Overbought/oversold indicator.",
    Candlesticks: "Shows open/high/low/close for each time period.",
    Confidence: "How confident the model is in its prediction.",
  };

  return (
    <div
      className={`min-h-screen font-[\'Exo 2\'],sans-serif ${
        darkMode ? "bg-black text-zinc-200" : "bg-zinc-100 text-zinc-900"
      } transition-colors duration-500`}
    >
      {showSplash && (
        <div
          className={`fixed inset-0 bg-black text-white flex items-center justify-center z-50 transition-opacity duration-1000 ${splashClass}`}
        >
          <h1 className="text-2xl font-bold tracking-wider transition-opacity duration-1000">
            Welcome to {flipA("Lattice | VANTHEON")}
          </h1>
        </div>
      )}

      <button
        onClick={() => setGlossaryOpen(true)}
        className="fixed bottom-4 right-4 bg-gray-700 text-gray-100 p-2 rounded-full shadow hover:bg-gray-600 transition"
      >
        ?
      </button>

      <GlossaryModal open={glossaryOpen} onClose={() => setGlossaryOpen(false)} darkMode={darkMode} />

      <Header darkMode={darkMode} toggleDarkMode={() => setDarkMode((prev) => !prev)} />

      <main
        className={`p-8 flex flex-col items-center text-sm transition-all duration-700 ease-out transform ${
          showSplash ? "opacity-0 scale-95" : "opacity-100 scale-100"
        }`}
      >
        <SearchBar
          ticker={ticker}
          setTicker={setTicker}
          loading={loading}
          getSignal={getSignal}
          darkMode={darkMode}
        />

        {loading && <Spinner />}

        <SignalSummary
          result={result}
          animatedConfidence={animatedConfidence}
          barWidth={barWidth}
          darkMode={darkMode}
        />

        <PredictionHistory history={history} setHistory={setHistory} darkMode={darkMode} />

        <LatticeControls
          ticker={ticker}
          setTicker={setTicker}
          getSignal={getSignal}
          range={range}
          setRange={setRange}
          showCandles={showCandles}
          setShowCandles={setShowCandles}
          showSMA={showSMA}
          setShowSMA={setShowSMA}
          showRSI={showRSI}
          setShowRSI={setShowRSI}
          showEMAs={showEMAs}
          setShowEMAs={setShowEMAs}
          darkMode={darkMode}
        />

        <ChartDisplay
          chartRef={chartRef}
          showCandles={showCandles}
          darkMode={darkMode}
          lineChartData={lineChartData}
          showSMA={showSMA}
          showEMAs={showEMAs}
          showRSI={showRSI}
          priceData={priceData}
          histError={histError}
        />
      </main>
    </div>
  );
}






