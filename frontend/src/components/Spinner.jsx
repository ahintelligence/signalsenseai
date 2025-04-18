import React from 'react';

export default function Spinner() {
  return (
    <div className="flex items-center justify-center mt-6">
      <div className="w-6 h-6 border-4 border-gray-500 border-dashed rounded-full animate-spin" />
    </div>
  );
}
