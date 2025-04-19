import React from 'react';
import FramedBox from "./FramedBox";

export default function SignalSummary({ result, barWidth, animatedConfidence, darkMode }) {
  if (!result || result.error) return null;

  const { signal, confidence, explanation, ticker } = result;

  const getSignalColor = () => {
    if (signal === "Buy") return "text-emerald-400";
    if (signal === "Sell" || signal === "Hold/Sell") return confidence > 75 ? "text-rose-400" : "text-yellow-300";
    return "text-yellow-300";
  };

  const getSignalBar = () => {
    if (signal === "Buy") return "bg-emerald-400";
    if (signal === "Sell" || signal === "Hold/Sell") return confidence > 75 ? "bg-rose-400" : "bg-yellow-300";
    return "bg-yellow-300";
  };

  return (
    <FramedBox darkMode={darkMode} className="w-full max-w-xl mb-10 shadow-md">
      <div className="flex justify-between items-baseline mb-2">
        <h2 className="text-2xl font-bold tracking-tight">{ticker}</h2>
        <p className={`text-lg font-medium ${getSignalColor()}`}>{signal}</p>
      </div>

      {/* Confidence */}
      <div className="mb-4">
        <p className="text-sm text-zinc-500 mb-1">Signal Confidence</p>
        <div className="w-full bg-zinc-700/40 h-3 rounded-none">
          <div
            className={`h-3 transition-all duration-700 ease-in-out ${getSignalBar()}`}
            style={{ width: `${barWidth}%` }}
          />
        </div>
        <p className="text-xs font-mono text-zinc-500 mt-1 tracking-tight">{animatedConfidence}%</p>
      </div>

      {/* Explanation */}
      <div className="mt-4 text-sm text-zinc-400">
        <h3 className="font-semibold mb-1">Explanation</h3>
        {explanation.split('. ').map((sentence, idx) => {
          const text = sentence.trim();
          if (!text) return null;
          const punctuated = text.endsWith('.') ? text : text + '.';
          return (
            <p key={idx} className="mb-2 leading-relaxed">
              {punctuated}
            </p>
          );
        })}
      </div>

      {/* Hint */}
      {signal === 'Buy' && (
        <p className="text-xs text-emerald-400 mt-2 font-mono">Price momentum upward detected.</p>
      )}
      {(signal === 'Sell' || signal === 'Hold/Sell') && (
        <p className="text-xs text-rose-400 mt-2 font-mono">Declining momentum. Consider exit.</p>
      )}
    </FramedBox>
  );
}





