/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#2563EB',
        secondary: '#059669',
        danger: '#DC2626',
        warning: '#D97706',
      }
    },
  },
  plugins: [],
}
