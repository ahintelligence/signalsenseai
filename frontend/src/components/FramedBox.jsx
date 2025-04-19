import React from "react";

export default function FramedBox({ children, darkMode, className = "", ...rest }) {
  return (
    <div
      className={`p-6 transition-all duration-300 ${darkMode ? "bg-zinc-900 text-zinc-200" : "bg-white text-zinc-800"} ${className}`}
      style={{
        border: "1px dotted",
        borderColor: darkMode ? "#52525b" : "#d4d4d8",
        borderRadius: "0px"
      }}
      {...rest}
    >
      {children}
    </div>
  );
}
