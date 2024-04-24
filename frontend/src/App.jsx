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
import { SidePanel } from "./components/SidePanel";
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
import { BillingPage } from "./components/BillingPage.jsx";

function MainApp({ loggedIn, setLoggedIn }) {
  let location = useLocation();

  const Nothing = () => {
    return <></>;
  };

  React.useEffect(() => {
    posthog.capture("$pageview");
  }, [location]);

  return (
    <>
      <NavHeader loggedIn={loggedIn} setLoggedIn={setLoggedIn} />
      <div className="container-fluid h-100 row">
        <div className="col-sm-12 col-md-3 col-xl-2" id="sidepanel">
          <SidePanel loggedIn={loggedIn} />
        </div>
        <div
          className="col-sm-12 col-md-9 col-xl-10 container-fluid"
          id="main-content"
        >
          <Routes>
            <Route path="/" element={loggedIn ? <Dashboard /> : <Nothing />} />
            <Route path="/frontpage" element={<Nothing />} />
            <Route
              path="/tests/*"
              element={<Dashboard loggedIn={loggedIn} />}
            />
            <Route path="/product" element={<ProductPage />} />
            <Route
              path="/pricing"
              element={<PricingPage loggedIn={loggedIn} />}
            />
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
            <Route
              path="/billing"
              element={<BillingPage loggedIn={loggedIn} />}
            />
            <Route path="*" element={<NoMatch />} />
          </Routes>
        </div>
        <div className="col-sm-12 container-fluid" id="main-content2">
          <Routes>
            <Route path="/" element={loggedIn ? <Nothing /> : <FrontPage />} />
            <Route path="/frontpage" element={<FrontPage />} />
            <Route path="*" element={<Nothing />} />
          </Routes>
        </div>
        <ScrollToTop />
        <Footer />
      </div>
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
