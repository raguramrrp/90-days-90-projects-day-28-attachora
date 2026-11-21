/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: '#F4F6F4',
        surface: '#FFFFFF',
        brand: {
          primary: '#286B50',
          hover: '#20553F',
          soft: '#E9F2EC',
          border: '#DCE3DE',
        },
        ink: {
          primary: '#202824',
          secondary: '#66716B',
          muted: '#8A948E',
        },
        table: {
          header: '#F7F9F7',
          hover: '#F1F6F2',
          border: '#EAEFEA',
        },
        status: {
          ready: '#278253',
          duplicate: '#66716B',
          review: '#B77925',
          filed: '#278253',
          failed: '#BD4545',
        }
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
