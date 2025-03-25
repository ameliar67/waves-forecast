import { createContext, useContext } from "react";
import { BuoyStation } from "./api";

export const StationsContext = createContext<Record<string, BuoyStation>>({});

export const useStations = () => useContext(StationsContext);
