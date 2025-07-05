import { createContext, useContext } from "react";
import { BeachLocation } from "./api";

export const StationsContext = createContext<Record<string, BeachLocation>>({});

export const useStations = () => useContext(StationsContext);
