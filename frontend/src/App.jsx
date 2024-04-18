import * as React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  useLocation,
} from "react-router-dom";
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
import { NoMatch } from "./components/NoMatch.jsx";
import posthog from "posthog-js";
import { AdminDashboard } from "./components/AdminDashboard.jsx";
import { PublicDashboard } from "./components/PublicDashboard.jsx";
import { OrgDashboard } from "./components/OrgDashboard.jsx";

const Root = ({ loggedIn }) => {
  return <>{loggedIn ? <Dashboard /> : <FrontPage />}</>;
};

function MainApp({ loggedIn, setLoggedIn }) {
  let location = useLocation();

  React.useEffect(() => {
    posthog.capture("$pageview");
  }, [location]);

  return (
    <>
      <NavHeader loggedIn={loggedIn} setLoggedIn={setLoggedIn} />
      <Routes>
        <Route path="/" element={<Root loggedIn={loggedIn} />} />
        <Route path="/tests/*" element={<Dashboard loggedIn={loggedIn} />} />
        <Route path="/product" element={<ProductPage />} />
        <Route path="/pricing" element={<PricingPage />} />
        <Route path="/legend" element={<LegendPage />} />
        <Route
          path="/signup"
          element={<SignUpPage setLoggedIn={setLoggedIn} />}
        />
        <Route path="/public/*" element={<PublicDashboard />} />
        <Route path="/orgs/*" element={<OrgDashboard />} />

        <Route
          path="/login"
          element={<Login loggedIn={loggedIn} setLoggedIn={setLoggedIn} />}
        />
        <Route path="/result/*" element={<SingleResult />} />
        <Route path="/docs/getting-started" element={<Docs />} />
        <Route path="/user/settings" element={<UserSettings />} />
        <Route path="/admin/*" element={<AdminDashboard />} />
        <Route path="*" element={<NoMatch />} />
      </Routes>
      <ScrollToTop />
      <Footer />
    </>
  );
}

function App() {
  const [loggedIn, setLoggedIn] = React.useState(() => {
    const saved = localStorage.getItem("loggedIn");
    const initialValue = JSON.parse(saved);
    return initialValue || false;
  });

  return (
    <>
      <Router>
        <MainApp loggedIn={loggedIn} setLoggedIn={setLoggedIn} />
      </Router>
    </>
  );
}

export default App;
