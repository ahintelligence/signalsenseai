/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Exo 2"', 'system-ui', 'sans-serif'], // Or replace "Inter" with "Rubik", etc.
      },
      colors: {
        zinc: require('tailwindcss/colors').zinc,
      }
    },
  
      
      animation: {
        fadeIn: 'fadeIn 0.5s ease-in-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: 0 },
          '100%': { opacity: 1 },
        },
      },
    },
  plugins: [],
};