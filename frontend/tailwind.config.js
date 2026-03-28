/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          navy:  "#0F172A",
          green: "#22C55E",
          teal:  "#0EA5E9",
          slate: "#1E293B",
        },
      },
      animation: {
        "fade-in":    "fadeIn 0.4s ease-in-out",
        "slide-up":   "slideUp 0.5s ease-out",
        "flip-in":    "flipIn 0.6s ease-out",
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      },
      keyframes: {
        fadeIn:  { "0%": { opacity: 0 }, "100%": { opacity: 1 } },
        slideUp: { "0%": { opacity: 0, transform: "translateY(20px)" }, "100%": { opacity: 1, transform: "translateY(0)" } },
        flipIn:  { "0%": { opacity: 0, transform: "rotateY(-15deg) scale(0.95)" }, "100%": { opacity: 1, transform: "rotateY(0) scale(1)" } },
      },
    },
  },
  plugins: [],
}
