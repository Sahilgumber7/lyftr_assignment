import React, { useEffect } from "react";

export function Toast({ message, onClose }) {
  useEffect(() => {
    if (!message) return;
    const timer = setTimeout(onClose, 2500);
    return () => clearTimeout(timer);
  }, [message, onClose]);

  if (!message) return null;

  return (
    <div className="fixed top-5 right-5 z-50">
      <div className="px-4 py-2 rounded-lg bg-black/80 border border-green-600/60 text-green-300 text-sm shadow-lg shadow-green-900/30 animate-slide-in">
        {message}
      </div>
    </div>
  );
}
