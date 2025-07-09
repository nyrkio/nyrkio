import * as React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  useLocation,
  useParams,
  useSearchParams
} from "react-router-dom";

import "./App.css";
import { Login } from "./components/Login.jsx";
import { Dashboard} from "./components/Dashboard.jsx";
import { FrontPage } from "./components/FrontPage.jsx";
import { NavHeader } from "./components/Nav.jsx";
import { SidePanel } from "./components/SidePanel";
import { Docs } from "./components/Docs.jsx";
import { DocsGraphs } from "./components/DocsGraphs.jsx";
import { DocsTeams } from "./components/DocsTeams.jsx";
import { ProductPage } from "./components/ProductPage.jsx";
import { AboutPage } from "./components/AboutPage.jsx";
import { LegalPage } from "./components/LegalPage.jsx";
import { LegendPage } from "./components/LegendPage.jsx";
import { EcosystemPage } from "./components/EcosystemPage.jsx";
import { PricingPage } from "./components/PricingPage.jsx";
import { ServicesPage } from "./components/ServicesPage.jsx";
import { SignUpPage } from "./components/SignUp.jsx";
import { Footer } from "./components/Footer.jsx";
import ScrollToTop from "./components/ScrollToTop.jsx";
import { UserSettings } from "./components/UserSettings.jsx";
import { OrgSettings } from "./components/OrgSettings.jsx";
import { NoMatch } from "./components/NoMatch.jsx";
import posthog from "posthog-js";
import { AdminDashboard } from "./components/AdminDashboard.jsx";
import { BillingPage } from "./components/BillingPage.jsx";
import { LogoSlogan, LogoSloganNarrow } from "./components/Logo";

function MainApp({ loggedIn, setLoggedIn }) {
  let location = useLocation();

  const Nothing = () => {
    return <></>;
  };

  React.useEffect(() => {
    posthog.capture("$pageview");
  }, [location]);

  const [searchParams,setSearchParams] = useSearchParams();
  let embed = searchParams.get("embed", "no");
  if(embed == "yes"){
    return (
    <>
      <div className="container-fluid h-100 row">
        <div
          className="col-sm-12 col-md-9 col-xl-10 container-fluid"
          id="main-content"
        >
          <Routes>
            <Route path="/" element={loggedIn ? <Dashboard embed={embed} path="/"/> : <Nothing />} />
            <Route path="/frontpage" element={<Nothing />} />
            <Route
              path="/tests/*"
              element={<Dashboard loggedIn={loggedIn} embed={embed} path="/tests/"/>}
            />
            <Route path="/product" element={<ProductPage />} />
            <Route
              path="/pricing"
              element={<PricingPage loggedIn={loggedIn} />}
            />
            <Route
              path="/services"
              element={<ServicesPage loggedIn={loggedIn} />}
            />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/about/ecosystem" element={<EcosystemPage />} />
            <Route path="/legal" element={<LegalPage />} />
            <Route path="/legend" element={<LegendPage />} />
            <Route
              path="/signup"
              element={<SignUpPage setLoggedIn={setLoggedIn} />}
            />
            <Route path="/public/*"
              element={<Dashboard loggedIn={loggedIn} embed={embed} path="/public/"/>}
            />
            <Route path="/org/*" element={<OrgSettings />} />
            <Route path="/orgs/*"
              element={<Dashboard loggedIn={loggedIn} embed={embed} path="/orgs/"/>}
            />
            <Route
              path="/login"
              element={<Login loggedIn={loggedIn} setLoggedIn={setLoggedIn} />}
            />
            <Route path="/result/*"
              element={<Dashboard loggedIn={loggedIn} embed={embed} path="/result/"/>}
            />
            <Route path="/docs/getting-started" element={<Docs />} />
            <Route path="/docs/working-with-graphs" element={<DocsGraphs />} />
            <Route path="/docs/teams" element={<DocsTeams />} />
            <Route path="/user/settings" element={<UserSettings />} />
            <Route path="/admin/*" element={<AdminDashboard embed={embed}/>} />
            <Route
              path="/billing"
              element={<BillingPage loggedIn={loggedIn} />}
            />
            <Route path="*" element={<NoMatch />} />
          </Routes>
        </div>
        <ScrollToTop />
      </div>
    </>
    )
  };




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
            <Route path="/" element={loggedIn ? <Dashboard path="/" /> : <Nothing />} />
            <Route path="/frontpage" element={<><LogoSloganNarrow /></>} />
            <Route
              path="/tests/*"
              element={<Dashboard loggedIn={loggedIn} path="/tests/" />}
            />
            <Route path="/product" element={<ProductPage />} />
            <Route
              path="/pricing"
              element={<PricingPage loggedIn={loggedIn} />}
            />
            <Route
              path="/services"
              element={<ServicesPage loggedIn={loggedIn} />}
            />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/about/ecosystem" element={<EcosystemPage />} />
            <Route path="/legal" element={<LegalPage />} />
            <Route path="/legend" element={<LegendPage />} />
            <Route
              path="/signup"
              element={<SignUpPage setLoggedIn={setLoggedIn} />}
            />
            <Route path="/public/*" element={<Dashboard path="/public/"/>} />
            <Route path="/org/*" element={<OrgSettings />} />
            <Route path="/orgs/*" element={<Dashboard path="/orgs/"/>} />
            <Route
              path="/login"
              element={<Login loggedIn={loggedIn} setLoggedIn={setLoggedIn} />}
            />
            <Route path="/result/*" element={<Dashboard path="/result/"/>} />
            <Route path="/docs/getting-started" element={<Docs />} />
            <Route path="/docs/working-with-graphs" element={<DocsGraphs />} />
            <Route path="/docs/teams" element={<DocsTeams />} />
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
            <Route path="/" element={loggedIn ? <Nothing /> : <><LogoSloganNarrow /><FrontPage /></>} />
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
