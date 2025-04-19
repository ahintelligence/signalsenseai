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
        canvas: "#000000", // solid black
        overlay: "#0f0f0f",
        cyanOverlay: "#00ffff22",
      },
      animation: {
        fadeIn: 'fadeIn 0.3s ease-out forwards', // Fade-in duration
        fadeOut: 'fadeOut 0.5s ease-in-out forwards', // Faster fade-out
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: 0, transform: 'translateY(10px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
        fadeOut: {
          '0%': { opacity: 1, transform: 'translateY(0)' },
          '100%': { opacity: 0, transform: 'translateY(-10px)' },
        },
      },
      transitionTimingFunction: {
        cold: 'cubic-bezier(0.25, 0.1, 0.25, 1)',
        smooth: 'cubic-bezier(0.68, -0.55, 0.27, 1.55)', // Smoother easing function
      },
      backdropBlur: {
        xs: '2px',
        sm: '4px',
        md: '8px',
        lg: '12px',
      },
    },
  },
  variants: {
    extend: {
      animation: ['motion-safe'],
    },
  },
  plugins: [],
};






