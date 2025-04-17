import React from "react";
import HelpTooltip from "./HelpTooltip";

export default function TooltipWord({ word, description }) {
  return (
    <span className="inline-flex items-center">
      {word}
      <HelpTooltip text={description} />
    </span>
  );
}
