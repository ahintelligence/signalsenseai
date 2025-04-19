import React from 'react';

export default function SearchBar({ ticker, setTicker, getSignal, loading = false, darkMode }) {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!ticker.trim()) return; // Prevent empty submissions
    getSignal(); // Only triggered on button click or Enter
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-3 mb-6 w-full max-w-xl">
      <input
        className={`flex-1 px-4 py-2 rounded-md border transition focus:outline-none ${
          darkMode
            ? "bg-zinc-900 text-zinc-100 border-zinc-700 placeholder-zinc-400 focus:ring-2 focus:ring-zinc-600"
            : "bg-white text-zinc-800 border-zinc-300 placeholder-zinc-500 focus:ring-2 focus:ring-zinc-200"
        }`}
        placeholder="Enter ticker (e.g. AAPL)"
        value={ticker}
        onChange={(e) => setTicker(e.target.value)}
      />
      <button
        type="submit"
        disabled={loading}
        className={`px-4 py-2 rounded-md transition ${
          darkMode
            ? "bg-zinc-800 text-zinc-200 hover:bg-zinc-700"
            : "bg-zinc-200 text-zinc-800 hover:bg-zinc-300"
        }`}
      >
        {loading ? "Loading..." : "Get Signal"}
      </button>
    </form>
  );
}

  
