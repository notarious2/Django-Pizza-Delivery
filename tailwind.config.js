/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["store/templates/store/*.{html,js}"],
  theme: {
    extend: {
      colors: {
        'dimly-blue': '#e8f9fd',
      },
    },
  },
  plugins: [],
}

