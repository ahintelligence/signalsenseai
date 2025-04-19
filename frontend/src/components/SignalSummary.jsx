import React from 'react';
import FramedBox from "./FramedBox";

export default function SignalSummary({ result, glossary = {}, barWidth, animatedConfidence, darkMode }) {
  if (!result || result.error) return null;

  const getSignalColor = (signal, confidence) => {
    if (signal === "Buy") return "text-emerald-400";
    if (signal === "Sell") return "text-rose-400";
    if (signal === "Hold" && confidence > 75) return "text-rose-400";
    return "text-yellow-300";
  };

  const getSignalBar = (signal, confidence) => {
    if (signal === "Buy") return "bg-emerald-400";
    if (signal === "Sell") return "bg-rose-400";
    if (signal === "Hold" && confidence > 75) return "bg-rose-400";
    return "bg-yellow-300";
  };

  const tokens = result.explanation?.split(/(\s+)/) || [];

  return (
    <FramedBox darkMode={darkMode} className="w-full max-w-xl mb-10 shadow-md">
      <div className="flex justify-between items-baseline mb-2">
        <h2 className="text-2xl font-bold tracking-tight">{result.ticker}</h2>
        <p className={`text-lg font-medium ${getSignalColor(result.signal, result.confidence)}`}>
          {result.signal}
        </p>
      </div>

      {/* Confidence */}
      <div className="mb-4">
        <p className="text-sm text-zinc-500 mb-1">Signal Confidence</p>
        <div className="w-full bg-zinc-700/40 h-3 rounded-none">
          <div
            className={`h-3 transition-all duration-700 ease-in-out ${getSignalBar(result.signal, result.confidence)}`}
            style={{ width: `${barWidth}%` }}
          />
        </div>
        <p className="text-xs font-mono text-zinc-500 mt-1 tracking-tight">
          {animatedConfidence}%
        </p>
      </div>

      {/* Explanation */}
      <p className="text-sm leading-relaxed text-zinc-400">
        {tokens.map((word, i) => {
          const clean = word.trim().toUpperCase();
          if (glossary[clean]) {
            return (
              <span key={i} className="relative group cursor-help">
                <span className="underline decoration-dotted underline-offset-2 text-zinc-300">
                  {word}
                </span>
                <span className="absolute bottom-full mb-1 hidden group-hover:block text-xs text-zinc-200 bg-zinc-800 px-2 py-1 shadow z-10 w-max max-w-xs rounded-none">
                  {glossary[clean]}
                </span>
              </span>
            );
          }
          return word;
        })}
      </p>

      {/* Hint */}
      {result.signal === 'Buy' && (
        <p className="text-xs text-emerald-400 mt-2 font-mono">Price momentum upward detected.</p>
      )}
      {result.signal === 'Sell' && (
        <p className="text-xs text-rose-400 mt-2 font-mono">Declining momentum. Consider exit.</p>
      )}
    </FramedBox>
  );
}




