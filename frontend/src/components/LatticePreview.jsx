// src/components/LatticePreview.jsx
import { Line } from "react-chartjs-2";
import { motion } from "framer-motion";

export default function LatticePreview({ portfolio, chartData, chartOptions, consoleLines }) {
  const smartInsight =
    portfolio?.active_signals >= 3
      ? "⚡ High activity detected. Multiple signals active — short-term opportunities likely."
      : "Steady conditions. Signal density within nominal thresholds.";

  const lines = portfolio ? (
    <>
      <p><strong>Assets Tracked:</strong> {portfolio.assets.join(", ")}</p>
      <p><strong>Volatility Clusters:</strong> {portfolio.volatility_clusters ? "Identified" : "None"}</p>
      <p><strong>Active Signals:</strong> {portfolio.active_signals}</p>
      <p><strong>Last Update:</strong> {portfolio.last_update}</p>
    </>
  ) : (
    <>
      <p><strong>Assets Tracked:</strong> TSLA, AAPL, ETH, USDJPY</p>
      <p><strong>Volatility Clusters:</strong> Identified</p>
      <p><strong>Active Signals:</strong> 3</p>
      <p><strong>Last Update:</strong> 2.3s ago</p>
    </>
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: consoleLines.length * 0.4 + 0.5 }}
      className="mt-6 bg-white/5 p-4 rounded-md border border-white/10"
    >
      <h3 className="text-white text-sm font-semibold mb-2 tracking-wide">LATTICE: Portfolio Intelligence</h3>
      <div className="text-green-300 text-xs leading-relaxed animate-pulse">
        {lines}
      </div>

      <div className="mt-4">
        <Line data={chartData} options={chartOptions} height={120} />
      </div>

      <div className="mt-4 text-xs text-white/60">
        Signal Feed: <span className="text-green-400 animate-pulse">[TSLA ↑ Buy] [ETH ↓ Watch] [AAPL ↔ Hold]</span>
      </div>

      <div className="mt-4 text-green-400 text-xs">
        <em>{smartInsight}</em>
      </div>
    </motion.div>
  );
}
