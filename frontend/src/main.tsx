import React from "react";
import ReactDOM from "react-dom/client";
import "@fontsource-variable/inter";
import { BrowserRouter } from "react-router-dom";
import { Toaster } from "sonner";
import App from "./app/App";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
      <Toaster position="bottom-right" richColors />
    </BrowserRouter>
  </React.StrictMode>,
);
