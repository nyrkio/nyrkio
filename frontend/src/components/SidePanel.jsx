import React, { useState } from "react";
import {
  Routes,
  Route,
  Link
} from "react-router-dom";

export const SidePanel = ({ loggedIn }) => {
  return (
    <div className="navbar-nav navbar-left justify-content-start">
      <Routes>
        <Route path="/" element={<FrontPageSidePanel loggedIn={loggedIn} />} />
        <Route path="/frontpage" element={<FrontPageSidePanel loggedIn={loggedIn} />} />
        <Route path="/tests/*" element={<FrontPageSidePanel loggedIn={loggedIn} />} />
        <Route path="/result/*" element={<FrontPageSidePanel loggedIn={loggedIn} />} />
        <Route path="/public/*" element={<FrontPageSidePanel loggedIn={loggedIn} />} />
        <Route path="/orgs/*" element={<FrontPageSidePanel loggedIn={loggedIn} />} />

        <Route path="/product" element={<ProductSidePanel  loggedIn={loggedIn} />} />
        <Route path="/product/*" element={<ProductSidePanel  loggedIn={loggedIn} />} />
        <Route path="/pricing" element={<PricingSidePanel  loggedIn={loggedIn} />} />
        <Route path="/docs/*" element={<DocsSidePanel loggedIn={loggedIn} />} />
        <Route path="/legend" element={<AboutSidePanel  loggedIn={loggedIn} />} />
        <Route path="/about*" element={<AboutSidePanel  loggedIn={loggedIn} />} />
        <Route path="/signup" element={<LoginSidePanel  loggedIn={loggedIn} />} />
        <Route path="/login" element={<LoginSidePanel  loggedIn={loggedIn} />} />
      </Routes>
    </div>
  );
};





const FrontPageSidePanel = ({ loggedIn }) => {
  if (loggedIn) {
    return (
      <>
        <Link to="/tests" className="nav-link">
          My Dashboard
        </Link>
        <Link to="/orgs" className="nav-link">
          Org Dashboards
        </Link>
        <Link to="/public" className="nav-link">
          Public Dashboards
        </Link>
        <Link to="/frontpage" className="nav-link">
          Front page
        </Link>
      </>
    );
  }
  // The default front page has no menu for visual reasons.
  // Login button is on the top right, which is the most important element.
  else {
    return (
      <></>
    );
  }
};

const ProductSidePanel = ({ loggedIn }) => {
    return (
      <>
        <Link to="/product" className="nav-link">
          Nyrkiö Change Detection
        </Link>
        <Link to="/public" className="nav-link">
          Public Dashboards<br /> from other users
        </Link>
      </>
    );
};
const PricingSidePanel = ({ loggedIn }) => {
    return (
      <></>
    );
};

const DocsSidePanel = ({ loggedIn }) => {

  return (
    <>
      <Link to="/docs/getting-started" className="nav-link">
        Getting started
      </Link>
      <div className="nav-link">
        <a href="/openapi">API</a>
      </div>
    </>
  );
};
const AboutSidePanel = ({ loggedIn }) => {
    return (
      <>
        <Link to="/about" className="nav-link">
          About Nyrkiö
        </Link>
        <Link to="/legend" className="nav-link">
          The Legend of Nyyrikki
        </Link>
      </>
    );
};
const LoginSidePanel = ({ loggedIn }) => {
    return (
      <>
        <Link to="/login" className="nav-link nav-link-login">
          Login
        </Link>
        <Link to="/signup" className="nav-link nav-link-login">
          Sign up
        </Link>
      </>
    );
};
