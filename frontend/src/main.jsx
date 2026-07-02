import ReactDOM from "react-dom/client";
import "bootstrap/dist/js/bootstrap.bundle.min.js";
import 'virtual:svg-icons-register';
import "./style/style.scss";
import App from "./App.jsx";
import posthog from "posthog-js";

posthog.init("phc_pj5OcqAS68hS0aIO0a3lqodk6lRekPEsz3VMdz6o7Z1", {
  api_host: "https://eu.posthog.com",
});

ReactDOM.createRoot(document.getElementById("root")).render(
  <App />
);
