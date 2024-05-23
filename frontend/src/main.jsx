import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import "./index.css";
import posthog from "posthog-js";

posthog.init("phc_pj5OcqAS68hS0aIO0a3lqodk6lRekPEsz3VMdz6o7Z1", {
  api_host: "https://eu.posthog.com",
});

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
