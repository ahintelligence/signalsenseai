import React from 'react';
import FramedBox from './FramedBox';

export default function PredictionHistory({ history, onClear, darkMode }) {
  const getSignalTextColor = (s) =>
    s === 'Buy' ? 'text-emerald-400' : s === 'Sell' ? 'text-rose-400' : 'text-yellow-300';

  return (
    <FramedBox darkMode={darkMode} className="w-full max-w-xl mb-8 shadow">
      <div className="flex justify-between items-center border-b border-dotted border-zinc-600 px-4 py-3">
        <h3 className="text-base font-semibold tracking-tight">Prediction History</h3>
        <button
          onClick={onClear}
          className={`text-sm font-mono transition ${
            darkMode ? 'text-zinc-400 hover:text-white' : 'text-zinc-500 hover:text-zinc-700'
          }`}
        >
          Clear
        </button>
      </div>

      <ul className="divide-y divide-dotted divide-zinc-800">
        {history.map((item, i) => (
          <li
            key={i}
            className={`p-4 flex justify-between items-center font-mono ${
              darkMode ? 'text-zinc-200' : 'text-zinc-800'
            }`}
          >
            <span className="font-medium">{item.ticker}</span>
            <span className={`text-sm font-medium ${getSignalTextColor(item.signal)}`}>
              {item.signal} ({item.confidence}%)
            </span>
          </li>
        ))}
      </ul>
    </FramedBox>
  );
}

