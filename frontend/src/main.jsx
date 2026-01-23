import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import "./index.css";
import posthog from "posthog-js";

/*
posthog.init("phc_pj5OcqAS68hS0aIO0a3lqodk6lRekPEsz3VMdz6o7Z1", {
  api_host: "https://eu.posthog.com",
});

*/

import { GoogleReCaptchaProvider } from 'react-google-recaptcha-v3';

ReactDOM.createRoot(document.getElementById("root")).render(
  <GoogleReCaptchaProvider
  reCaptchaKey="6LehQ1IsAAAAACQWFomHKj-zBF_cMG91fWzk4nlh"
  scriptProps={{
    async: true, // optional, default to false,
    defer: false, // optional, default to false
    appendTo: 'head', // optional, default to "head", can be "head" or "body",
    nonce: undefined // optional, default undefined
  }}
  container={{ // optional to render inside custom element
    element: "recaptchabutton",
    parameters: {
      badge: 'inline', // optional, default undefined
      theme: 'light', // optional, default undefined
    }
  }}
  >
  <App />
  </GoogleReCaptchaProvider>,
);
