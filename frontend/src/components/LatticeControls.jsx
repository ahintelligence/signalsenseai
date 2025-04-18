// src/components/LatticeControls.jsx
export default function LatticeControls({
    ticker,
    setTicker,
    getSignal,
    range,
    setRange,
    showCandles,
    setShowCandles,
    showSMA,
    setShowSMA,
    showRSI,
    setShowRSI,
    showEMAs,
    setShowEMAs,
    darkMode,
  }) {
    const ranges = [
      { label: '1M', value: '1mo' },
      { label: '3M', value: '3mo' },
      { label: '6M', value: '6mo' },
      { label: 'YTD', value: 'ytd' },
      { label: '1Y', value: '1y' },
    ];
  
    return (
      <div className="w-full max-w-xl mb-6 flex flex-wrap gap-4 items-center justify-center">
        <h3 className="text-lg font-semibold w-full text-center">Price Chart ({range})</h3>
  
        {ranges.map((r) => (
          <button
            key={r.value}
            onClick={() => {
                setRange(r.value);
              }}              
            className={`px-3 py-1 rounded text-sm transition ${
              range === r.value
                ? darkMode
                  ? "bg-gray-700 text-gray-100"
                  : "bg-gray-900 text-gray-100"
                : darkMode
                ? "bg-gray-800 text-gray-300"
                : "bg-gray-200 text-gray-700"
            }`}
          >
            {r.label}
          </button>
        ))}
  
        <label className="flex items-center gap-2">
          <input type="checkbox" checked={showCandles} onChange={() => setShowCandles(!showCandles)} />
          Candlesticks
        </label>
  
        <label className="flex items-center gap-2">
          <input type="checkbox" checked={showSMA} onChange={() => setShowSMA(!showSMA)} />
          SMA 20
        </label>
  
        {Object.entries(showEMAs).map(([k, v]) => (
          <label key={k} className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={v}
              onChange={() => setShowEMAs((prev) => ({ ...prev, [k]: !prev[k] }))}
            />
            {k.toUpperCase()}
          </label>
        ))}
        
  
        <label className="flex items-center gap-2">
          <input type="checkbox" checked={showRSI} onChange={() => setShowRSI(!showRSI)} />
          RSI
        </label>
        
      </div>
      
      

    );
  }
  
