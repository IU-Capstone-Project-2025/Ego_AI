import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { General } from "./screens/General/General";
import { Calendar } from "./screens/userInterface/Calendar";
import OtherPage from "./screens/OtherPage";
import { RegPage } from "./screens/RegistrationPage/RegPage";
import { LoginCallback } from "./screens/LoginCallback";
import { TestCallback } from "./screens/TestCallback/TestCallback";
import { ProtectedRoute } from "./components/ProtectedRoute";
import "./index.css";
import { Layout } from './components/Layout';

createRoot(document.getElementById("app") as HTMLElement).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<General />} />
        <Route path="/reg-page" element={<RegPage />} />
        <Route path="/login/callback" element={<LoginCallback />} />
        <Route path="/test-callback" element={<TestCallback />} />
        <Route path="/other" element={<OtherPage />} />
        <Route path="/calendar" element={
          <ProtectedRoute>
            <Layout>
              <Calendar />
            </Layout>
          </ProtectedRoute>
        } />
      </Routes>
    </BrowserRouter>
  </StrictMode>,
);
