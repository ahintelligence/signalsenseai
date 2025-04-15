import React, { useState, useEffect, useRef } from "react";

function App() {
  const [ticker, setTicker] = useState("");
  const [result, setResult] = useState(null);
  const [barWidth, setBarWidth] = useState(0);
  const [animatedConfidence, setAnimatedConfidence] = useState(0);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const prevTicker = useRef("");

  const getSignal = async () => {
    if (!ticker) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch(`http://localhost:8000/predict/${ticker.toUpperCase()}`);
      const data = await res.json();
      setResult(data);
      if (!data.error) {
        setHistory((prev) => [...prev, data]);
      }
    } catch (err) {
      setResult({ error: "Failed to fetch signal. Check server or ticker symbol." });
    } finally {
      setLoading(false);
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

  return (
    <div
      className={`min-h-screen font-sans transition-colors duration-300 ease-in-out ${
        darkMode ? "bg-[#121212] text-white" : "bg-[#f5f5f5] text-gray-900"
      }`}
    >
      {/* Header */}
      <header
        className={`border-b px-8 py-4 flex justify-between items-center shadow-sm transition-colors duration-300 ease-in-out ${
          darkMode ? "bg-[#1e1e1e]" : "bg-white"
        }`}
      >
        <h1
          className={`text-2xl font-semibold tracking-tight transition-colors duration-300 ${
            darkMode ? "text-white" : "text-gray-900"
          }`}
        >
          SignalSense AI
        </h1>
        <button
          onClick={() => setDarkMode(!darkMode)}
          className="px-4 py-2 rounded shadow text-sm font-medium transition 
            bg-gray-700 text-white hover:bg-gray-600 dark:bg-gray-300 dark:text-gray-900 dark:hover:bg-gray-200"
        >
          {darkMode ? "Light Mode" : "Dark Mode"}
        </button>
      </header>

      {/* Main */}
      <main className="p-8 flex flex-col items-center transition-colors duration-300 ease-in-out">
        <div className="flex gap-3 mb-10">
          <input
            className={`px-4 py-2 border rounded-lg shadow-sm focus:outline-none focus:ring-2 w-64 placeholder-gray-400 text-sm transition-colors duration-300
              ${
                darkMode
                  ? "bg-[#2a2a2a] text-white border-gray-600 focus:ring-gray-500"
                  : "bg-white text-gray-900 border-gray-300 focus:ring-gray-300"
              }`}
            placeholder="Enter ticker (e.g. AAPL)"
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
          />
          <button
            className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors duration-300
              ${
                loading
                  ? "bg-gray-400 text-white"
                  : darkMode
                  ? "bg-gray-100 text-black hover:bg-gray-200"
                  : "bg-gray-900 text-white hover:bg-gray-800"
              }`}
            onClick={getSignal}
            disabled={loading}
          >
            {loading ? "Loading..." : "Get Signal"}
          </button>
        </div>

        {loading && <Spinner />}

        {/* Result */}
        {result && (
          <div
            className={`rounded-xl shadow-lg p-6 w-full max-w-xl animate-fadeIn mb-10 transition-colors duration-300 ease-in-out ${
              darkMode ? "bg-[#1f1f1f]" : "bg-white"
            }`}
          >
            {result.error ? (
              <p className="text-red-500 font-semibold">{result.error}</p>
            ) : (
              <>
                <div className="flex items-baseline justify-between mb-2">
                  <h2
                    className={`text-2xl font-bold transition-colors duration-300 ${
                      darkMode ? "text-white" : "text-gray-900"
                    }`}
                  >
                    {result.ticker}
                  </h2>
                  <p
                    className={`text-lg font-medium transition-colors duration-300 ease-in-out ${getSignalTextColor(
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
                    ></div>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">{animatedConfidence}%</p>
                </div>

                <p className="text-sm leading-relaxed text-gray-700 dark:text-gray-300 transition-colors duration-300 ease-in-out">
                  {result.explanation}
                </p>
              </>
            )}
          </div>
        )}

        {/* History */}
        {history.length > 0 && (
          <div className="mt-4 w-full max-w-xl transition-colors duration-300 ease-in-out">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300 transition-colors duration-300 ease-in-out">
                Prediction History
              </h3>
              <button
                onClick={() => setHistory([])}
                className="text-sm text-gray-500 hover:text-gray-800 dark:hover:text-white transition"
              >
                Clear History
              </button>
            </div>
            <ul className="space-y-3">
              {history.map((item, idx) => (
                <li
                  key={idx}
                  className={`p-4 rounded-lg shadow flex justify-between items-center transition-colors duration-300 ease-in-out ${
                    darkMode ? "bg-[#1e1e1e] text-white" : "bg-white text-gray-900"
                  }`}
                >
                  <span className="font-semibold">{item.ticker}</span>
                  <span
                    className={`text-sm font-medium transition-colors duration-300 ease-in-out ${getSignalTextColor(
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
      </main>
    </div>
  );
}

export default App;
