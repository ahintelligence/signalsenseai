import { useState, useEffect, useRef } from "react";

export function useSignalLogic() {
  const [ticker, setTicker] = useState("");
  const [range, setRange] = useState("1mo");
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [priceData, setPriceData] = useState([]);
  const [barWidth, setBarWidth] = useState(0);
  const [animatedConfidence, setAnimatedConfidence] = useState(0);
  const [loading, setLoading] = useState(false);
  const [histError, setHistError] = useState(null);
  const prevTicker = useRef("");

  const getSignal = async (symbolInput, onComplete) => {
    const symbol = typeof symbolInput === "string" ? symbolInput : ticker;

    if (!symbol || typeof symbol !== "string") {
      const err = { error: "Please enter a valid ticker symbol." };
      setResult(err);
      return err;
    }

    setLoading(true);

    try {
      const res = await fetch(`/predict/${symbol.toUpperCase()}`);
      const text = await res.text();

      if (!res.ok) {
        let message = "An unknown error occurred.";
        if (res.status === 404) {
          message = `No data found for "${symbol.toUpperCase()}". The stock might be delisted or invalid.`;
        } else if (res.status >= 500) {
          message = "Server error. Please try again later.";
        }

        const err = { error: message };
        setResult(err);
        return err;
      }

      const data = JSON.parse(text);
      setResult(data);

      if (!data.error) {
        setHistory((prev) => [...prev, data]);
      }

      await fetchHistory(symbol, range);

      if (typeof onComplete === "function") onComplete();

      return data;
    } catch (err) {
      console.error("Error in getSignal:", err);
      const fallback = {
        error: "Something went wrong. Please check your connection or try again.",
      };
      setResult(fallback);
      return fallback;
    } finally {
      setLoading(false);
    }
  };

  const fetchHistory = async (symbol, selectedRange) => {
    try {
      const res = await fetch(`/history/${symbol}?range=${selectedRange}`);
      const json = await res.json();

      if (!res.ok || !json.history) {
        throw new Error(json?.error || "Failed to load chart history.");
      }

      setHistError(null);
      setPriceData(json.history);
    } catch (e) {
      setHistError(e.message);
      setPriceData([]);
    }
  };

  useEffect(() => {
    if (result && !result.error && result.ticker !== prevTicker.current) {
      setBarWidth(0);
      requestAnimationFrame(() =>
        requestAnimationFrame(() => setBarWidth(result.confidence))
      );

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

  useEffect(() => {
    if (prevTicker.current) {
      fetchHistory(prevTicker.current, range);
    }
  }, [range]);

  return {
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
  };
}

  

