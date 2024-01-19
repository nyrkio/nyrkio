import { createContext, useEffect, useState } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link,
  useLocation,
} from "react-router-dom";
import "./App.css";
import { Login, LogOut, LoginButton } from "./components/Login.jsx";
import { Dashboard, SingleResult } from "./components/Dashboard.jsx";

const LoggedInContext = createContext(false);

function NoMatch() {
  return (
    <div style={{ padding: 20 }}>
      <h2>404: Page Not Found</h2>
      <p>Lorem ipsum dolor sit amet, consectetur adip.</p>
    </div>
  );
}

async function loginUser(credentials) {
  return fetch("http://localhost:8000/auth/jwt/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: JSON.stringify(credentials),
  }).then((data) => data.json());
}

const NavigationItems = () => {
  return (
    <>
      <button
        className="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarSupportedContent"
        aria-controls="navbarSupportedContent"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span className="navbar-toggler-icon"></span>
      </button>
      <div className="collapse navbar-collapse" id="navbarSupportedContent">
        <ul className="navbar-nav me-auto mb-2 mb-lg-0">
          <li className="nav-item">
            <a className="nav-link" href="#">
              Company
            </a>
          </li>
          <li className="nav-item">
            <a className="nav-link" href="#">
              Product
            </a>
          </li>
          <li className="nav-item">
            <a className="nav-link" href="#">
              Pricing
            </a>
          </li>
          <li className="nav-item">
            <a className="nav-link" href="#">
              Services
            </a>
          </li>
          <li className="nav-item">
            <a className="nav-link" href="#">
              Research
            </a>
          </li>
        </ul>
      </div>
    </>
  );
};

const NavHeader = ({ loggedIn, setLoggedIn }) => {
  return (
    <nav className="navbar navbar-expand-lg">
      <div className="container-fluid">
        <NavigationItems />
        {loggedIn ? <LogOut setLoggedIn={setLoggedIn} /> : <LoginButton />}
      </div>
    </nav>
  );
};

const Banner = () => {
  return (
    <div className="container-fluid border p-5 text-center">
      <h1>Detect every performance change.</h1>
      <h5>
        The performance measurement tool that harnesses the power of change
        point detection
      </h5>
    </div>
  );
};

const FeatureHighlight = () => {
  return (
    <div className="row">
      <div className="col-sm-4">
        <h3>Shift left</h3>
        <p>
          Performance regressions are often only discovered during later stages
          of development such as release candidate testing.
        </p>
        <p>
          Pull your performance testing earlier with Nyrkiö and flag regressions
          as soon as they're committed.
        </p>
      </div>
      <div className="col-sm-4">
        <h3>Automate analysis</h3>
        <p>
          Avoid the tedious work of checking performance dashboards by hand.
        </p>
      </div>
      <div className="col-sm-4">
        <h3>State of the art</h3>
        <p>
          Change point detection is state of the art technology for detecting
          changes in software performance. Used by leading technology companies
          such all around the world including MongoDB and Netflix.
        </p>
      </div>
    </div>
  );
};

const SignUpButton = () => {
  const [showForm, setShowForm] = useState(false);
  const handleSignUpClick = () => {
    setShowForm(true);
    console.log("Sign up clicked");
  };
  if (showForm) {
    return (
      <div className="row mt-5">
        <div className="col-sm-6 offset-sm-3">
          <form>
            <div className="mb-3">
              <label htmlFor="exampleInputEmail1" className="form-label">
                Email address
              </label>
              <input
                type="email"
                className="form-control"
                id="exampleInputEmail1"
              />
              <div id="emailHelp" className="form-text">
                We'll never share your email with anyone else.
              </div>
            </div>
            <button type="submit" className="btn btn-success">
              Submit
            </button>
          </form>
        </div>
      </div>
    );
  } else {
    return (
      <div className="row mt-5">
        <div className="d-flex justify-content-center">
          <button className="btn btn-success" onClick={handleSignUpClick}>
            Sign Up
          </button>
        </div>
      </div>
    );
  }
};

const Root = ({ loggedIn }) => {
  return (
    <>
      <div className="container mt-5 text-center">
        {loggedIn ? (
          <Dashboard />
        ) : (
          <>
            <Banner />
            <FeatureHighlight />
            <SignUpButton />
          </>
        )}
      </div>
    </>
  );
};

function App() {
  const [count, setCount] = useState(0);
  const [token, setToken] = useState();
  console.log("Resetting");
  const [loggedIn, setLoggedIn] = useState(() => {
    const saved = localStorage.getItem("loggedIn");
    const initialValue = JSON.parse(saved);
    console.log("Reading " + saved);
    return initialValue || false;
  });

  return (
    <>
      <Router>
        <NavHeader loggedIn={loggedIn} setLoggedIn={setLoggedIn} />
        <Routes>
          <Route path="/" element={<Root loggedIn={loggedIn} />} />
          <Route
            path="/login"
            element={<Login loggedIn={loggedIn} setLoggedIn={setLoggedIn} />}
          />
          <Route path="/result" element={<SingleResult />} />
          <Route path="*" element={<NoMatch />} />
        </Routes>
      </Router>
    </>
  );
}

export default App;
