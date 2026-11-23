/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          navy: '#071B3A',
          deep: '#040d1e',
          royal: '#2563EB',
          sky: '#38BDF8',
          cyan: '#06B6D4',
          teal: '#14B8A6',
          emerald: '#10B981',
          light: '#F4F9FF',
          darkSurface: '#0b192c',
          darkCard: 'rgba(11, 25, 48, 0.7)'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      animation: {
        'float-slow': 'float 14s ease-in-out infinite',
        'float-medium': 'float 9s ease-in-out infinite',
        'float-fast': 'float 6s ease-in-out infinite',
        'pulse-subtle': 'pulseSubtle 4s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px) scale(1)' },
          '50%': { transform: 'translateY(-20px) scale(1.04)' },
        },
        pulseSubtle: {
          '0%, 100%': { opacity: '0.35' },
          '50%': { opacity: '0.65' },
        }
      }
    },
  },
  plugins: [],
}
