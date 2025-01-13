import { BrowserRouter, Route, Routes } from "react-router";
import { HomePage } from "./Home";
import { ForecastPage } from "./ForecastPage";

export function App() {
    return <BrowserRouter>
        <Routes>
            <Route index element={<HomePage />} />
            <Route path="/forecast/:locationId" element={<ForecastPage />} />
        </Routes>
    </BrowserRouter>;
}