import { useState } from "react";
import "./App.css";

const LoginButton = () => {
  const [loggedIn, setLoggedIn] = useState(false);
  const handleLogoutClick = () => {
    // console.log(loggedIn);
    loggedIn ? setLoggedIn(false) : setLoggedIn(true);
  };
  if (!loggedIn) {
    return (
      <>
        <a href="/login" className="btn me-2">
          Log In
        </a>
        <button className="btn btn-success" type="submit">
          Sign Up
        </button>
      </>
    );
  } else {
    return (
      <>
        <button className="btn btn-success" onClick={handleLogoutClick}>
          Log Out
        </button>
      </>
    );
  }
};

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

const NavHeader = () => {
  return (
    <nav className="navbar navbar-expand-lg">
      <div className="container-fluid">
        <NavigationItems />
        <LoginButton />
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

function App() {
  const [count, setCount] = useState(0);

  return (
    <>
      <NavHeader />
      <Banner />
      <div className="container mt-5">
        <FeatureHighlight />
        <SignUpButton />
      </div>
    </>
  );
}

export default App;
