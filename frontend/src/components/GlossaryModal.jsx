import React from "react";

export default function GlossaryModal({ open, onClose, darkMode, glossary = {} }) {
  return (
    <div
      className={`fixed inset-0 z-50 flex items-center justify-center transition-opacity duration-300 ${
        open ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"
      } bg-black/50`}
      onClick={onClose}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className={`transform transition-all duration-300 w-full max-w-md p-6 border text-sm font-mono ${
          open ? "scale-100 opacity-100" : "scale-95 opacity-0"
        } ${darkMode ? "bg-zinc-900 text-zinc-100 border-zinc-600" : "bg-white text-zinc-900 border-zinc-300"}`}
        style={{
          borderStyle: "dotted",
          borderRadius: "0px",
        }}
      >
        <h2 className="text-base font-semibold mb-4 tracking-tight border-b border-dotted pb-2">
          Glossary
        </h2>
        <ul className="space-y-2">
          {Object.entries(glossary).map(([term, def]) => (
            <li key={term}>
              <strong className="text-zinc-300">{term}</strong>: <span className="text-zinc-400">{def}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}




