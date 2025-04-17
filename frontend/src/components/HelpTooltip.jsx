import React from "react";

export default function HelpTooltip({ text }) {
  return (
    <span className="relative inline-block group ml-1">
      {/* small question‑mark icon */}
      <svg
        className="w-4 h-4 inline-block text-gray-500 hover:text-gray-700"
        viewBox="0 0 20 20"
        fill="currentColor"
      >
        <path d="M9 7h2v2H9V7zM9 11h2v2H9v-2zm1-9a9 9 0 100 18A9 9 0 0010 2zm0 16a7 7 0 110-14 7 7 0 010 14z" />
      </svg>

      {/* tooltip text — also a span so we never introduce a div in a p */}
      <span
        className="
          absolute 
          bottom-full 
          left-1/2 
          transform -translate-x-1/2 
          mb-1 
          px-2 py-1 
          text-xs 
          bg-gray-800 text-white 
          rounded 
          opacity-0 
          group-hover:opacity-100 
          transition-opacity
          whitespace-nowrap
        "
      >
        {text}
      </span>
    </span>
  );
}

