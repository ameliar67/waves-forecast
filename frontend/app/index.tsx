import { createRoot } from "react-dom/client";
import { App } from "./App";

const mountElement = document.getElementById("root")!;
const reactRoot = createRoot(mountElement);
reactRoot.render(<App />);
