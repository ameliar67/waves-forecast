import { useEffect, useState } from "react";
import { BrowserRouter, Route, Routes } from "react-router";
import { ForecastPage } from "./ForecastPage";
import { HomePage } from "./Home";
import { BuoyStation } from "./LocationData";

export function App() {
    // State to store the fetched station data
    const [stations, setStations] = useState<Record<string, BuoyStation>>({});

    // Fetch station data from the backend API when the component loads
    useEffect(() => {
        const fetchStations = async () => {
            try {
                const response = await fetch('/api/locations');  // Adjust the URL if necessary
                if (!response.ok) {
                    throw new Error('Failed to fetch station data');
                }

                const data = await response.json();
                setStations(data?.locations || {});  // Set the fetched stations into state
            } catch (error) {
                console.error('Error fetching station data:', error);
            }
        };

        fetchStations(); // Call the fetch function
    }, []); // Empty dependency array to run this effect only once when the component mounts

    return <BrowserRouter>
        <Routes>
            <Route index element={<HomePage stations={stations} />} />
            <Route path="/forecast/:locationId" element={<ForecastPage stations={stations} />} />
        </Routes>
    </BrowserRouter>;
}