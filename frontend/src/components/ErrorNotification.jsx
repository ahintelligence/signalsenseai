import React, { useState, useEffect } from "react";

export default function ErrorNotification({ message, onClose, darkMode }) {
  const [fadeIn, setFadeIn] = useState(false); // For fade-in
  const [fadeOut, setFadeOut] = useState(false); // For fade-out

  useEffect(() => {
    // Trigger fade-in when the message is shown
    setFadeIn(true);

    // After 3.5 seconds, trigger fade-out
    const fadeOutTimer = setTimeout(() => {
      setFadeOut(true); // Trigger fade-out after 3.5 seconds
    }, 3500); // Fade out after 3.5 seconds

    // Close the toast after 4 seconds
    const removeTimer = setTimeout(() => {
      if (onClose) onClose(); // Call onClose to remove toast after 4 seconds
    }, 4000);

    // Cleanup timers on component unmount or change
    return () => {
      clearTimeout(fadeOutTimer);
      clearTimeout(removeTimer);
    };
  }, [onClose]);

  return (
    <div
      className={`fixed top-6 left-1/2 transform -translate-x-1/2 z-50 px-4 py-3 rounded border text-sm font-mono shadow-md
        transition-all duration-500
        ${fadeIn ? "opacity-100 animate-fadeIn" : "opacity-0"}  // Fade-in animation
        ${fadeOut ? "opacity-0 animate-fadeOut" : ""}
        ${darkMode
          ? "bg-red-950 text-red-300 border-red-500"
          : "bg-red-100 text-red-800 border-red-400"
        }`}
    >
      <strong className="mr-1">Error:</strong> {message}
    </div>
  );
}












