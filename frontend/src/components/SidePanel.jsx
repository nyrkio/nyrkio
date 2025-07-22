import React, { useState } from "react";
import { Routes, Route, Link } from "react-router-dom";

export const SidePanel = ({ loggedIn }) => {
  return (
    <div className="navbar-nav navbar-left justify-content-start">
      <Routes>
        <Route path="/" element={<FrontPageSidePanel loggedIn={loggedIn} />} />
        <Route path="/dash" element={<DashSidePanel loggedIn={loggedIn} />} />

        <Route
          path="/frontpage"
          element={<FrontPageSidePanel loggedIn={loggedIn} />}
        />
        <Route
          path="/tests/*"
          element={<DashSidePanel loggedIn={loggedIn} />}
        />
        <Route
          path="/result/*"
          element={<DashSidePanel loggedIn={loggedIn} />}
        />
        <Route
          path="/public/*"
          element={<DashSidePanel loggedIn={loggedIn} />}
        />
        <Route
          path="/orgs/*"
          element={<DashSidePanel loggedIn={loggedIn} />}
        />

        <Route
          path="/product"
          element={<ProductSidePanel loggedIn={loggedIn} />}
        />
        <Route
          path="/product/*"
          element={<ProductSidePanel loggedIn={loggedIn} />}
        />
        <Route
          path="/pricing/*"
          element={<ProductSidePanel loggedIn={loggedIn} />}
        />
        <Route
          path="/services"
          element={<ProductSidePanel loggedIn={loggedIn} />}
        />
        <Route path="/docs/*" element={<DocsSidePanel loggedIn={loggedIn} />} />
        <Route
          path="/legend"
          element={<AboutSidePanel loggedIn={loggedIn} />}
        />
        <Route
          path="/about/*"
          element={<AboutSidePanel loggedIn={loggedIn} />}
        />
        <Route
          path="/legal/*"
          element={<AboutSidePanel loggedIn={loggedIn} />}
        />
        <Route
          path="/signup"
          element={<LoginSidePanel loggedIn={loggedIn} />}
        />
        <Route path="/login" element={<LoginSidePanel loggedIn={loggedIn} />} />
      </Routes>
    </div>
  );
};

const FrontPageSidePanel = ({ loggedIn }) => {
  document.body.classList.add("section-front");
  if (loggedIn) {
    return (
      <>
      </>
    );
  }
  // The default front page has no menu for visual reasons.
  // Login button is on the top right, which is the most important element.
  else {
    return <></>;
  }
};

const DashSidePanel = ({ loggedIn }) => {
  document.body.classList.add("section-front");
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
    return (<>
    <Link to="/docs/getting-started" className="nav-link">
    Create My Dashboard
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
};

const ProductSidePanel = ({ loggedIn }) => {
  document.body.classList.add("section-product");
  return (
    <>
      <Link to="/product" className="nav-link">
      Nyrkiö Change Detection
      </Link>
      <Link to="/product/user-testimonials" className="nav-link">
      What our users say
      </Link>
      <Link to="/pricing" className="nav-link">
      Pricing
      </Link>
      <Link to="/services" className="nav-link">
      Services
      </Link>
      <Link to="/public" className="nav-link">
        Public Dashboards
        <br /> from other users
      </Link>
    </>
  );
};

const DocsSidePanel = ({ loggedIn }) => {
  document.body.classList.add("section-docs");

  return (
    <>
      <Link to="/docs/getting-started" className="nav-link">
        Getting started
      </Link>
      <Link to="/docs/getting-started#getting-started-github-action" className="nav-link nav-level2">
        GitHub action
      </Link>
      <Link to="/docs/getting-started#getting-started-curl" className="nav-link nav-level2">
        Generic HTTP / curl
      </Link>

      <Link to="/docs/working-with-graphs" className="nav-link">
      Working with the graphs
      </Link>
      <Link to="/docs/git-perf-plugin" className="nav-link">
        git-perf plugin
      </Link>

      <Link to="/docs/teams" className="nav-link">
        Teams / Orgs
      </Link>
      <div className="nav-link">
        <a href="/openapi">API</a>
      </div>
    </>
  );
};
const AboutSidePanel = ({ loggedIn }) => {
  document.body.classList.add("section-about");
  return (
    <>
      <Link to="/about" className="nav-link">
        About Nyrkiö Oy
      </Link>
      <Link to="/about/ecosystem" className="nav-link">
      Open Source Ecosystem
      </Link>
      <Link to="/legal" className="nav-link">
      Legal
      </Link>
      <Link to="/legend" className="nav-link">
        The Legend of Nyyrikki
      </Link>
    </>
  );
};
const LoginSidePanel = ({ loggedIn }) => {
  document.body.classList.add("section-login");
  return (
    <>
      <Link to="/login" className="nav-link nav-link-login">
        Login
      </Link>
      <Link to="/signup" className="nav-link nav-link-login">
        Create account
      </Link>
    </>
  );
};
