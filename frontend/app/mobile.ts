import { useLayoutEffect, useState } from "react";

const match = window.matchMedia("(max-width:800px)");
const listeners: ((match: boolean) => void)[] = [];

match.addEventListener("change", (e) => {
  for (const l of listeners) {
    l(e.matches);
  }
});

export function useIsMobile() {
  const [isMobile, setIsMobile] = useState(match.matches);
  useLayoutEffect(() => {
    listeners.push(setIsMobile);
    return () => {
      const index = listeners.indexOf(setIsMobile);
      listeners.splice(index, 1);
    };
  }, []);

  return isMobile;
}
