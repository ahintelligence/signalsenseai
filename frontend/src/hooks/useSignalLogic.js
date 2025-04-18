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
      console.error("❌ Invalid ticker symbol");
      return;
    }
  
    setLoading(true); // ← make sure loading starts here
  
    try {
      const res = await fetch(`/predict/${symbol.toUpperCase()}`);
      const text = await res.text();
      console.log("🧾 Raw response text:", text);
  
      const data = JSON.parse(text);
      setResult(data);
  
      if (!data.error) setHistory((prev) => [...prev, data]);
      await fetchHistory(symbol, range);
  
      // ✅ Trigger animation-ready logic
      if (typeof onComplete === "function") {
        onComplete();
      }
    } catch (err) {
      console.error("Error in getSignal:", err);
      setResult({ error: "Failed to fetch signal." });
    } finally {
      setLoading(false);
    }
  };
  

  const fetchHistory = async (symbol, selectedRange) => {
    try {
      const res = await fetch(`/history/${symbol.toUpperCase()}?range=${selectedRange}`);
      const json = await res.json();
      if (!res.ok) {
        setHistError(json.error || `Error ${res.status}`);
        setPriceData(json.history || []);
      } else {
        setHistError(null);
        setPriceData(json.history || []);
      }
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
    if (ticker) {
      fetchHistory(ticker, range);
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
