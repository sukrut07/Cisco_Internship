import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#111317",
        surface: "#111317",
        "surface-container": "#1e2023",
        "surface-container-high": "#282a2e",
        "surface-container-low": "#191b1f",
        "surface-variant": "#23262a",
        "on-background": "#e2e2e6",
        "on-surface": "#e2e2e6",
        "on-surface-variant": "#c4c6d0",
        outline: "#8e9099",
        "outline-variant": "#44474e",
        primary: "#ffb59a",
        "primary-container": "#ff7a33",
        "inverse-primary": "#a73a00",
        secondary: "#a5e7ff",
        "secondary-fixed": "#b6ebff",
        tertiary: "#4edea3",
        error: "#ffb4ab",
        orange: {
          400: "#ffa170",
          500: "#ff7a33",
          600: "#e56424",
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      borderRadius: {
        DEFAULT: '0.375rem',
        sm: '0.25rem',
        md: '0.375rem',
        lg: '0.5rem',
        xl: '0.75rem',
        '2xl': '1rem',
        '3xl': '1.25rem',
        full: '9999px',
      },
      boxShadow: {
        'glow-critical': '0 0 20px rgba(255, 122, 51, 0.35)',
        'glow-warning': '0 0 20px rgba(251, 191, 36, 0.35)',
        'glow-cyan': '0 0 20px rgba(165, 231, 255, 0.25)',
        'glow-emerald': '0 0 20px rgba(78, 222, 163, 0.25)',
      },
      transitionDuration: {
        '150': '150ms',
        '250': '250ms',
      },
      transitionTimingFunction: {
        'out': 'cubic-bezier(0, 0, 0.2, 1)',
        'in-out': 'cubic-bezier(0.4, 0, 0.2, 1)',
      },
      keyframes: {
        pulseIndicator: {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%': { opacity: '0.4', transform: 'scale(1.25)' },
        },
        glowPulse: {
          '0%, 100%': { opacity: '0.6' },
          '50%': { opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(6px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideInRight: {
          '0%': { opacity: '0', transform: 'translateX(16px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        spinSlow: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        }
      },
      animation: {
        'pulse-indicator': 'pulseIndicator 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow-pulse': 'glowPulse 3s ease-in-out infinite',
        'fadeIn': 'fadeIn 250ms cubic-bezier(0, 0, 0.2, 1) both',
        'slideInRight': 'slideInRight 250ms cubic-bezier(0, 0, 0.2, 1) both',
        'spin-slow': 'spinSlow 8s linear infinite',
      }
    },
  },
  plugins: [],
}

export default config
