/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#060911',
        sidebar: '#0a0e1a',
        surface: {
          50: '#1e293b',
          100: '#0f172a',
          800: '#0d1322',
          900: '#090d16',
          950: '#060911',
        },
        cyan: {
          400: '#22d3ee',
          500: '#06b6d4',
          300: '#67e8f9',
          950: '#083344',
        },
        emerald: {
          400: '#34d399',
          500: '#10b981',
          300: '#6ee7b7',
          950: '#022c22',
        },
        purple: {
          400: '#c084fc',
          500: '#a855f7',
          300: '#d8b4fe',
          950: '#3b0764',
        },
        brand: {
          primary: '#00f2fe',
          secondary: '#4facfe',
          accent: '#10b981',
          violet: '#7c3aed',
        }
      },
      boxShadow: {
        'glass-sm': '0 4px 20px 0 rgba(0, 0, 0, 0.45)',
        'glass-lg': '0 8px 32px 0 rgba(0, 0, 0, 0.65)',
        'glow-cyan': '0 0 25px -3px rgba(6, 182, 212, 0.45)',
        'glow-emerald': '0 0 25px -3px rgba(16, 185, 129, 0.45)',
        'glow-purple': '0 0 25px -3px rgba(168, 85, 247, 0.45)',
        'glow-blue': '0 0 25px -3px rgba(59, 130, 246, 0.45)',
      },
      animation: {
        'marquee': 'marquee 30s linear infinite',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 5s ease-in-out infinite',
        'shimmer': 'shimmer 2s infinite',
      },
      keyframes: {
        marquee: {
          '0%': { transform: 'translateX(0%)' },
          '100%': { transform: 'translateX(-50%)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-6px)' },
        },
        shimmer: {
          '100%': { transform: 'translateX(100%)' }
        }
      }
    },
  },
  plugins: [],
}
