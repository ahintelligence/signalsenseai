
// src/components/Header.jsx
import React from "react";

function flipA(text) {
    return text.replace(/A/g, 'Ʌ');
  }

export default function Header({ darkMode, toggleDarkMode }) {
    return (
      <header className="px-6 py-4 bg-black text-gray-100 flex justify-between items-center">
        <h1 className="text-xl font-semibold tracking-tight">
  {flipA("Lattice | VANTHEON")}
</h1>

        <button
          onClick={toggleDarkMode}
          className="px-4 py-2 rounded bg-zinc-800 text-gray-300 hover:bg-zinc-700 transition"
        >
          {darkMode ? "Light" : "Dark"}
        </button>
      </header>
    );
  }
  
