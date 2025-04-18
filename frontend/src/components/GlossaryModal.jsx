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
        className={`transform transition-all duration-300 p-6 rounded shadow-lg w-full max-w-md ${
          open ? "scale-100 opacity-100" : "scale-95 opacity-0"
        } ${darkMode ? "bg-zinc-900 text-zinc-100" : "bg-white text-zinc-900"}`}
      >
        <h2 className="text-lg font-semibold mb-4">Glossary</h2>
        <ul className="space-y-2 text-sm">
          {Object.entries(glossary).map(([term, def]) => (
            <li key={term}>
              <strong className="font-medium">{term}:</strong> {def}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}



