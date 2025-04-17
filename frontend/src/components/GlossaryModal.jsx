import React from "react";

export default function GlossaryModal({ open, onClose, glossary, darkMode }) {
  if (!open) return null;
  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center"
      onClick={onClose}
    >
      <div
        className={`bg-white dark:bg-gray-800 p-6 rounded shadow-lg max-w-md w-full`}
        onClick={e => e.stopPropagation()}
      >
        <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-gray-100">
          Glossary
        </h2>
        <ul className="space-y-2">
          {Object.entries(glossary).map(([term, desc]) => (
            <li key={term}>
              <strong className="text-gray-800 dark:text-gray-200">{term}:</strong>{" "}
              <span className="text-gray-600 dark:text-gray-400">{desc}</span>
            </li>
          ))}
        </ul>
        <button
          onClick={onClose}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded"
        >
          Close
        </button>
      </div>
    </div>
  );
}
