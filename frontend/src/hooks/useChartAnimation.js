import { useState, useEffect } from "react";

export function useChartAnimation(priceData, showSMA, range) {
  const [smaAnimatedData, setSmaAnimatedData] = useState([]);

  useEffect(() => {
    if (!showSMA || !priceData.length) {
      setSmaAnimatedData([]);
      return;
    }

    const full = priceData
      .filter((d) => d.sma20 != null)
      .map((d) => ({ Date: d.date, Close: +d.close, SMA20: +d.sma20 }));

    let i = 0;
    const animate = () => {
      if (i <= full.length) {
        setSmaAnimatedData(full.slice(0, i));
        i++;
        requestAnimationFrame(animate);
      }
    };

    animate();
  }, [priceData, showSMA, range]);

  return smaAnimatedData;
}
