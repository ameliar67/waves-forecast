import React, { useEffect, useState } from "react";
import { useParams } from "react-router";

export const ForecastPage: React.FC = () => {
    const { locationId } = useParams();
    const [forecastData, setForecastData] = useState<any>(null);

    useEffect(() => {
        setForecastData(null);

        (async function () {
            const response = await fetch(`/api/forecast/${locationId}`);
            const data = await response.json();
            setForecastData(data);
        })();
    }, [locationId]);

    return <div>{forecastData ? <img src={`data:image/png;base64,${forecastData!.wave_height_graph}`} /> : "Loading"}</div>;
};
