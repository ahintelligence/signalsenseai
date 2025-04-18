import React from 'react';

export default function SignalSummary({
  result,
  glossary = {},
  barWidth,
  animatedConfidence,
  darkMode,
}) {
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
    <div
      className={`rounded-xl p-6 w-full max-w-xl mb-10 shadow-md border transition-colors duration-300 ${
        darkMode
          ? "bg-zinc-900 border-zinc-800 text-zinc-100"
          : "bg-white border-zinc-200 text-zinc-800"
      }`}
    >
      <div className="flex justify-between items-baseline mb-2">
        <h2 className="text-2xl font-bold tracking-tight">{result.ticker}</h2>
        <p className={`text-lg font-medium ${getSignalColor(result.signal, result.confidence)}`}>
          {result.signal}
        </p>
      </div>

      {/* Confidence bar */}
      <div className="mb-4">
        <p className={`text-sm mb-1 ${darkMode ? "text-zinc-400" : "text-gray-500"}`}>Confidence</p>
        <div className={`${darkMode ? "bg-zinc-700" : "bg-gray-300"} w-full rounded-full h-3`}>
          <div
            className={`h-3 rounded-full transition-all duration-700 ease-in-out ${getSignalBar(result.signal)}`}
            style={{ width: `${result.confidence}%` }}
          />
        </div>
        <p className={`text-xs font-mono mt-1 tracking-tight ${darkMode ? "text-zinc-400" : "text-gray-500"}`}>
          {result.confidence}%
        </p>
      </div>

      {/* Explanation with glossary tooltips */}
      <p className="text-sm leading-relaxed mb-2">
        {tokens.map((word, i) => {
          const clean = word.trim().toUpperCase();
          if (glossary[clean]) {
            return (
              <span key={i} className="relative group cursor-help">
                <span className="underline decoration-dotted underline-offset-2">{word}</span>
                <span
                  className={`absolute bottom-full mb-1 hidden group-hover:block text-xs ${
                    darkMode ? "bg-zinc-700 text-white" : "bg-gray-200 text-black"
                  } p-1 rounded shadow z-10`}
                >
                  {glossary[clean]}
                </span>
              </span>
            );
          }
          return word;
        })}
      </p>

      {/* Hints */}
      {result.signal === "Buy" && (
        <p className="text-xs text-emerald-400 mt-2">Indicates a likely price increase.</p>
      )}
      {result.signal === "Sell" && (
        <p className="text-xs text-rose-400 mt-2">Indicates a potential price decline.</p>
      )}
    </div>
  );
}

