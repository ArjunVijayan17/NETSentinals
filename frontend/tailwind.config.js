/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: "#0f1117",
          soft: "#161a24",
          line: "#232936",
          mute: "#8b93a7",
        },
        accent: "#00d4aa",
        danger: "#ef4444",
        safe: "#22c55e",
      },
    },
  },
  plugins: [],
};
