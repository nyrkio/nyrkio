import { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import "./App.css";
import { Login } from "./components/Login.jsx";
import { Dashboard, SingleResult } from "./components/Dashboard.jsx";
import { FrontPage } from "./components/FrontPage.jsx";
import { NavHeader } from "./components/Nav.jsx";
import { Docs } from "./components/Docs.jsx";
import { ProductPage } from "./components/ProductPage.jsx";
import { LegendPage } from "./components/LegendPage.jsx";
import { PricingPage } from "./components/PricingPage.jsx";
import { SignUpPage } from "./components/SignUp.jsx";
import { Footer } from "./components/Footer.jsx";
import ScrollToTop from "./components/ScrollToTop.jsx";
import { UserSettings } from "./components/UserSettings.jsx";

function NoMatch() {
  return (
    <div className="container text-center justify-content-center p-5">
      <h2>404: Page Not Found</h2>
    </div>
  );
}

const Root = ({ loggedIn }) => {
  return <>{loggedIn ? <Dashboard /> : <FrontPage />}</>;
};

function App() {
  const [loggedIn, setLoggedIn] = useState(() => {
    const saved = localStorage.getItem("loggedIn");
    const initialValue = JSON.parse(saved);
    return initialValue || false;
  });

  return (
    <>
      <Router>
        <NavHeader loggedIn={loggedIn} setLoggedIn={setLoggedIn} />
        <Routes>
          <Route path="/" element={<Root loggedIn={loggedIn} />} />
          <Route
            path="/tests/:prefix"
            element={<Dashboard loggedIn={loggedIn} />}
          />
          <Route path="/product" element={<ProductPage />} />
          <Route path="/pricing" element={<PricingPage />} />
          <Route path="/legend" element={<LegendPage />} />
          <Route path="/signup" element={<SignUpPage />} />

          <Route
            path="/login"
            element={<Login loggedIn={loggedIn} setLoggedIn={setLoggedIn} />}
          />
          <Route path="/result/:testName" element={<SingleResult />} />
          <Route path="/docs/getting-started" element={<Docs />} />
          <Route path="/user/settings" element={<UserSettings />} />
          <Route path="*" element={<NoMatch />} />
        </Routes>
        <ScrollToTop />
        <Footer />
      </Router>
    </>
  );
}

export default App;
