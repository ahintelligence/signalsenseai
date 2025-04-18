import React from 'react';

export default function PredictionHistory({ history, onClear, darkMode }) {
  const getSignalTextColor = (s) =>
    s === 'Buy' ? 'text-emerald-400' : s === 'Sell' ? 'text-rose-400' : 'text-yellow-300';

  return (
    <div
      className={`w-full max-w-xl mb-8 rounded-lg border shadow ${
        darkMode
          ? 'bg-zinc-900 border-zinc-800 text-zinc-100'
          : 'bg-white border-zinc-200 text-zinc-800'
      }`}
    >
      <div className="flex justify-between items-center border-b px-4 py-3">
        <h3 className="text-base font-semibold tracking-tight">Prediction History</h3>
        <button
          onClick={onClear}
          className={`text-sm transition ${
            darkMode ? 'text-zinc-400 hover:text-white' : 'text-zinc-500 hover:text-zinc-700'
          }`}
        >
          Clear
        </button>
      </div>

      <ul className="divide-y divide-zinc-800">
        {history.map((item, i) => (
          <li
            key={i}
            className={`px-4 py-3 flex justify-between items-center ${
              darkMode ? 'hover:bg-zinc-800' : 'hover:bg-zinc-100'
            }`}
          >
            <span className="font-medium">{item.ticker}</span>
            <span className={`text-sm font-medium ${getSignalTextColor(item.signal)}`}>
              {item.signal} ({item.confidence}%)
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
