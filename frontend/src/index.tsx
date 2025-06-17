import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { General } from "./screens/General/General";

createRoot(document.getElementById("app") as HTMLElement).render(
  <StrictMode>
    <General />
  </StrictMode>,
);
