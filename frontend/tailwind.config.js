// tailwind.config.js
import colors from 'tailwindcss/colors';

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Exo 2"', 'system-ui', 'sans-serif'],
      },
      colors: {
        zinc: colors.zinc,
      },
      animation: {
        fadeIn: 'fadeIn 0.5s ease-out forwards',
        fadeInDelayed1: 'fadeIn 0.5s ease-out 0.2s forwards',
        fadeInDelayed2: 'fadeIn 0.5s ease-out 0.4s forwards',
        fadeInDelayed3: 'fadeIn 0.5s ease-out 0.6s forwards',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: 0, transform: 'translateY(10px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
};
