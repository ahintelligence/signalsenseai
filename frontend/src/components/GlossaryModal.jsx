// src/components/GlossaryModal.jsx
export default function GlossaryModal({ open, onClose, glossary = {}, darkMode }) {
  return (
    <div
      className={`fixed inset-0 bg-black/60 flex items-center justify-center z-50 transition-opacity ${
        open ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"
      }`}
    >
      <div className={`p-6 rounded shadow max-w-md w-full ${darkMode ? "bg-gray-800 text-white" : "bg-white text-black"}`}>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Glossary</h2>
          <button onClick={onClose} className="text-sm hover:underline">
            Close
          </button>
        </div>

        <div className="space-y-2 max-h-[60vh] overflow-y-auto">
          {Object.entries(glossary).map(([term, description]) => (
            <div key={term}>
              <p className="font-bold">{term}</p>
              <p className="text-sm text-gray-400">{description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

