/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        gold: {
          DEFAULT: '#D4AF37',
          light:   '#F4E4BA',
          dark:    '#996515',
        },
        teal:    '#00CED1',
        coral:   '#FF6B6B',
        emerald: '#2ECC71',
        amber:   '#F39C12',
        purple:  '#9B59B6',
      },
      animation: {
        'float-slow':   'floatSlow 8s ease-in-out infinite',
        'float-medium': 'floatMed 6s ease-in-out infinite',
        'float-fast':   'floatFast 4s ease-in-out infinite',
        'pulse-slow':   'pulse 4s cubic-bezier(0.4,0,0.6,1) infinite',
        'bar-rise':     'barRise 0.5s ease-out both',
        'count-up':     'countUp 0.6s ease-out both',
      },
      keyframes: {
        floatSlow:  { '0%,100%': { transform: 'translateY(0)' }, '50%': { transform: 'translateY(-30px)' } },
        floatMed:   { '0%,100%': { transform: 'translateY(0)' }, '50%': { transform: 'translateY(-20px)' } },
        floatFast:  { '0%,100%': { transform: 'translateY(0)' }, '50%': { transform: 'translateY(-12px)' } },
        barRise:    { from: { transform: 'scaleY(0)', opacity: 0 }, to: { transform: 'scaleY(1)', opacity: 1 } },
        countUp:    { from: { opacity: 0, transform: 'translateY(8px)' }, to: { opacity: 1, transform: 'translateY(0)' } },
      },
      backdropBlur: {
        xs: '2px',
      },
      screens: {
        '2xl': '1400px',
        '3xl': '1600px',
      },
    },
  },
  plugins: [],
}
