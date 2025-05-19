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
      { label: "1M", value: "1mo" },
      { label: "3M", value: "3mo" },
      { label: "6M", value: "6mo" },
      { label: "YTD", value: "ytd" },
      { label: "1Y", value: "1y" },
    ];
  
    const resetIndicators = () => {
      setShowCandles(true);
      setShowSMA(false);
      setShowRSI(false);
      setShowEMAs({
        ema9: true,
        ema20: false,
        ema50: false,
        ema100: false,
        ema200: false,
      });
    };
  
    return (
      <div className="w-full max-w-xl mb-6 flex flex-col gap-4 items-center">
        <h3 className="text-lg font-semibold text-center">
          Price Chart ({range.toUpperCase()})
        </h3>
  
        {/* Range Selector */}
        <div className="flex flex-wrap justify-center gap-2">
          {ranges.map((r) => (
            <button
              key={r.value}
              onClick={() => {
                setRange(r.value);
                getSignal(ticker);
              }}
              className={`px-3 py-1 rounded text-sm transition ${
                range === r.value
                  ? darkMode
                    ? "bg-gray-700 text-white"
                    : "bg-gray-900 text-white"
                  : darkMode
                  ? "bg-gray-800 text-gray-300"
                  : "bg-gray-200 text-gray-700"
              }`}
            >
              {r.label}
            </button>
          ))}
        </div>
  
        {/* Overlay Toggles */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-sm">
          <label title="Display candlestick chart" className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={showCandles}
              onChange={() => setShowCandles(!showCandles)}
            />
            Candlesticks
          </label>
  
          <label title="Simple Moving Average (20 days)" className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={showSMA}
              onChange={() => setShowSMA(!showSMA)}
            />
            SMA 20
          </label>
  
          {Object.entries(showEMAs).map(([key, value]) => (
            <label
              key={key}
              title={`Exponential Moving Average (${key.replace("ema", "")} days)`}
              className="flex items-center gap-2"
            >
              <input
                type="checkbox"
                checked={value}
                onChange={() =>
                  setShowEMAs((prev) => ({ ...prev, [key]: !prev[key] }))
                }
              />
              {key.toUpperCase()}
            </label>
          ))}
  
          <label title="Relative Strength Index (RSI)" className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={showRSI}
              onChange={() => setShowRSI(!showRSI)}
            />
            RSI
          </label>
        </div>
  
        {/* Reset Button */}
        <button
          onClick={resetIndicators}
          className="mt-2 px-4 py-1.5 text-sm font-medium rounded transition text-white bg-rose-600 hover:bg-rose-700"
        >
          Reset to Default
        </button>
      </div>
    );
  }
  
  
