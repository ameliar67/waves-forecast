import { createRoot } from "react-dom/client";
import '../styles/globals.css';
import { App } from "./App";

const mountElement = document.getElementById("root")!;
const reactRoot = createRoot(mountElement);
reactRoot.render(<App />);
