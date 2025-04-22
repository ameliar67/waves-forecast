import { createContext, useContext } from "react";

export interface ConvertableUnit {
  suffix: string;
  name: string;
  convert: (value: number) => number;
}

export interface UnitConversions {
  systemName: string;
  distance: ConvertableUnit;
  temperature: ConvertableUnit;
}

export const MetricConversions: UnitConversions = {
  systemName: "Metric",
  distance: {
    suffix: "m",
    name: "meters",
    convert: (v) => v,
  },
  temperature: {
    suffix: "°C",
    name: "Celsius",
    convert: (v) => ((v - 32) * 5) / 9,
  },
};

export const ImperialConversions: UnitConversions = {
  systemName: "US Imperial",
  distance: {
    suffix: "ft",
    name: "feet",
    convert: (v) => 3.281 * v,
  },
  temperature: {
    suffix: "°F",
    name: "Farenheit",
    convert: (v) => v,
  },
};

export function formatUnit(
  value: number,
  unit: ConvertableUnit,
  precision?: number
) {
  const displayValue =
    precision === undefined
      ? unit.convert(value)
      : unit.convert(value).toFixed(precision);
  return `${displayValue} ${unit.suffix}`;
}

export const UnitsContext = createContext<UnitConversions>(MetricConversions);

export const useUnits = () => useContext(UnitsContext);
