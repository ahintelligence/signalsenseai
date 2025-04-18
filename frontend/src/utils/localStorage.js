// src/utils/localStorage.js

export const getStored = (key, fallback) => {
    try {
      const v = localStorage.getItem(key);
      return v ? JSON.parse(v) : fallback;
    } catch {
      return fallback;
    }
  };
  
  export const setStored = (key, val) => {
    try {
      localStorage.setItem(key, JSON.stringify(val));
    } catch {}
  };
  