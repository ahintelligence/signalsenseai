// src/components/InterfaceSection.jsx
import { useEffect, useState } from "react";
import LatticePreview from "./LatticePreview";


const fallbackConsoleLines = [
  "[SYSTEM] Initializing interface...",
  "[VANTH-CORE] Intelligence modules loaded.",
  "[LATTICE] Volatility matrix parsed. Portfolio systems online.",
  "[ACCESS] Standing by.",
];

export default function InterfaceSection() {
  const [consoleLines, setConsoleLines] = useState(fallbackConsoleLines);
  const [portfolio, setPortfolio] = useState(null);
  const [historyData, setHistoryData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const summaryRes = await fetch("http://localhost:8000/api/summary");
        const summary = await summaryRes.json();
        setPortfolio(summary);

        const historyRes = await fetch("http://localhost:8000/history/AAPL?range=6mo");
        const history = await historyRes.json();
        const closes = history?.prices?.map((d) => d.close).slice(-30) || [];
        setHistoryData(closes);

        setConsoleLines([
          "[SYSTEM] Initializing interface...",
          "[VANTH-CORE] Intelligence modules loaded.",
          "[LATTICE] Fetching live data from lattice backend...",
          "[ACCESS] Standing by.",
        ]);
      } catch (error) {
        console.error("Error fetching Lattice data:", error);
        setConsoleLines(fallbackConsoleLines);
        setPortfolio(null);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const chartData = {
    labels: historyData.map((_, i) => `T-${historyData.length - i}`),
    datasets: [
      {
        label: "AAPL 6mo",
        data: historyData,
        fill: true,
        backgroundColor: "rgba(0,255,170,0.1)",
        borderColor: "#00FFAA",
        tension: 0.4,
        pointRadius: 0,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: { mode: "index", intersect: false },
    },
    scales: {
      x: { display: false },
      y: { display: false },
    },
  };

  return (
    <section id="interface" className="h-screen snap-start bg-black flex flex-col items-center justify-center px-4">
      <div className="w-full max-w-3xl bg-black text-green-400 font-mono text-sm border border-white/10 p-6 shadow-lg backdrop-blur-md">
        <h2 className="text-white text-xl mb-4 font-semibold tracking-wider border-b border-white/10 pb-2">
          LATTICE PREVIEW: ECONOMIC INTELLIGENCE
        </h2>

        {consoleLines.map((line, i) => (
          <p key={i} className="leading-relaxed">
            {line}
          </p>
        ))}

        <LatticePreview
          portfolio={portfolio}
          chartData={chartData}
          chartOptions={chartOptions}
          consoleLines={consoleLines}
        />

        <div className="mt-6 text-center">
          <a
            href="http://localhost:5173/"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block text-green-300 text-xs tracking-wide hover:text-white hover:underline transition-all"
          >
            → Launch Full LATTICE Console ↗
          </a>
          <p className="text-white/40 text-[0.65rem] mt-1">
            Dive into predictive analytics, signal history, and real-time economic analysis.
          </p>
        </div>
      </div>
    </section>
  );
}


