import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Builds into ../static/site so the FastAPI app can serve the landing
// page with zero Node.js at runtime. Asset URLs are relative ("./")
// so the page works behind any host or subpath.
export default defineConfig({
  plugins: [react()],
  base: "./",
  build: {
    outDir: "../static/site",
    emptyOutDir: true,
  },
});
