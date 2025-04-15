import { createRoot } from "react-dom/client";
import "../styles/globals.css";
import { App } from "./App";
import "@fontsource/inter/700.css";
import "@fontsource/inter/400.css";
import "@fontsource/inter/600.css";
import "@fontsource/inter/500.css";

const mountElement = document.getElementById("root")!;
const reactRoot = createRoot(mountElement);
reactRoot.render(<App />);
