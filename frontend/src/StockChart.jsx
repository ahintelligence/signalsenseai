// src/components/StockChart.jsx
import React from "react";
import { ChartCanvas, Chart } from "react-stockcharts";
import {
  CandlestickSeries,
  XAxis,
  YAxis,
  CrossHairCursor,
  MouseCoordinateX,
  MouseCoordinateY,
  EdgeIndicator,
  ZoomButtons,
  OHLCTooltip,
  discontinuousTimeScaleProvider,
} from "react-stockcharts/lib";
import { fitWidth } from "react-stockcharts/lib/helper";
import { timeParse } from "d3-time-format";

const parseDate = timeParse("%Y-%m-%d");

function StockChart({ data, width, ratio, height = 400 }) {
  const parsedData = data.map(d => ({
    ...d,
    date: parseDate(d.Date),
  }));

  const xScaleProvider = discontinuousTimeScaleProvider.inputDateAccessor(d => d.date);
  const { data: chartData, xScale, xAccessor, displayXAccessor } = xScaleProvider(parsedData);
  const start = xAccessor(chartData[chartData.length - 100]);
  const end = xAccessor(chartData[chartData.length - 1]);
  const xExtents = [start, end];

  return (
    <ChartCanvas
      height={height}
      ratio={ratio}
      width={width}
      margin={{ left: 50, right: 50, top: 10, bottom: 30 }}
      type="svg"
      seriesName="Data"
      data={chartData}
      xScale={xScale}
      xAccessor={xAccessor}
      displayXAccessor={displayXAccessor}
      xExtents={xExtents}
    >
      <Chart id={1} yExtents={d => [d.high, d.low]}>
        <XAxis />
        <YAxis />
        <CandlestickSeries />
        <MouseCoordinateX displayFormat={d => d.toLocaleDateString()} />
        <MouseCoordinateY />
        <EdgeIndicator itemType="last" orient="right" edgeAt="right" yAccessor={d => d.close} />
        <OHLCTooltip origin={[0, 0]} />
        <ZoomButtons />
      </Chart>
      <CrossHairCursor />
    </ChartCanvas>
  );
}

export default fitWidth(StockChart);
