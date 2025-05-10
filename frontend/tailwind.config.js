/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
      './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
      './src/components/**/*.{js,ts,jsx,tsx,mdx}',
      './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    theme: {
      extend: {
        animation: {
          'slideDown': 'slideDown 0.2s ease-out',
          'fade-in': 'fadeIn 0.3s ease-in-out',
        },
        keyframes: {
          slideDown: {
            '0%': { maxHeight: '0', opacity: '0' },
            '100%': { maxHeight: '1000px', opacity: '1' },
          },
          fadeIn: {
            '0%': { opacity: '0' },
            '100%': { opacity: '1' },
          },
        },
        colors: {
          'primary-background': '#1A1A1A',
          'secondary-background': '#242424',
          'secondary-text': '#A3A3A3',
        },
      },
    },
    plugins: [],
  }
  