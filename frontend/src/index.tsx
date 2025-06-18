import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { General } from "./screens/General/General";
import OtherPage from "./screens/OtherPage";

createRoot(document.getElementById("app") as HTMLElement).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<General />} />
        <Route path="/other" element={<OtherPage />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>,
);
