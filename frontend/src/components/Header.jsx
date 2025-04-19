import React from "react";

function flipA(text) {
  return text.replace(/A/g, 'Ʌ');
}

export default function Header({ darkMode, toggleDarkMode, onOpenGlossary }) {
  return (
    <header className="px-6 py-4 bg-black text-zinc-100 flex justify-between items-center border-b border-zinc-800">
      <h1 className="text-xl font-semibold tracking-tight">
        {flipA("Lattice | VANTHEON")}
      </h1>

      <div className="flex items-center gap-2">
        <button
          onClick={toggleDarkMode}
          className="px-3 py-1 border border-dotted text-sm hover:border-white hover:text-white transition"
        >
          {darkMode ? "Light" : "Dark"}
        </button>
        <button
          onClick={onOpenGlossary}
          className="px-3 py-1 border border-dotted text-sm hover:border-white hover:text-white transition"
        >
          Glossary
        </button>
      </div>
    </header>
  );
}

  
