import * as React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
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
import { DocsCurl } from "./components/DocsCurl.jsx";
import { DocsGraphs } from "./components/DocsGraphs.jsx";
import { DocsGitPerfPlugin } from "./components/DocsGitPerfPlugin.jsx";
import { DocsTeams } from "./components/DocsTeams.jsx";
import { ProductPage } from "./components/ProductPage.jsx";
import { UsersPage } from "./components/UsersPage.jsx";
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

const Nothing = () => {
  return <></>;
};

function MainApp({ loggedIn, setLoggedIn }) {
  let location = useLocation();


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
        <RouteMap embed={embed} loggedIn={loggedIn} setLoggedIn={setLoggedIn} />
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
        <RouteMap embed={embed} loggedIn={loggedIn} setLoggedIn={setLoggedIn} />
        </div>
        <div className="col-sm-12 container-fluid" id="main-content2">
          <Routes>
            <Route path="/" element={loggedIn ? <Nothing /> : <><LogoSlogan /><FrontPage loggedIn={loggedIn}/></>} />
            <Route path="/frontpage" element={<><LogoSlogan /><FrontPage loggedIn={loggedIn}/></>} />
            <Route path="*" element={<Nothing />} />
          </Routes>
        </div>
        <ScrollToTop />
        <Footer />
      </div>
    </>
  );
}

function RouteMap({loggedIn, embed, setLoggedIn, }) {
  return (
    <Routes>
      <Route path="/" element={loggedIn ? <Navigate to="/tests"/> : <Navigate to="/frontpage" />} />
      <Route path="/dash" element={loggedIn ? <Navigate to="/tests"/> : <Navigate to="/public"/> } />
      <Route path="/frontpage" element={<Nothing />} />
      <Route
      path="/tests/*"
      element={<Dashboard loggedIn={loggedIn} embed={embed} path="/tests/"/>}
      />
      <Route path="/product" element={<ProductPage />} />
      <Route path="/product/user-testimonials" element={<UsersPage />} />
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
      <Route path="/docs/getting-started-http" element={<DocsCurl />} />
      <Route path="/docs/working-with-graphs" element={<DocsGraphs />} />
      <Route path="/docs/git-perf-plugin" element={<DocsGitPerfPlugin />} />
      <Route path="/docs/teams" element={<DocsTeams />} />
      <Route path="/user/settings" element={<UserSettings />} />
      <Route path="/admin/*" element={<AdminDashboard embed={embed}/>} />
      <Route
      path="/billing"
      element={<BillingPage loggedIn={loggedIn} />}
      />
      <Route path="*" element={<NoMatch />} />
    </Routes>
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
