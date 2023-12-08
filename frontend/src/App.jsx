import { useState } from "react";
import "./App.css";

const Button = () => {
  const [count, setCount] = useState(0);
  const loggedIn = true;
  if (!loggedIn) {
    return (
      <>
        <button class="btn" type="submit">
          Log In
        </button>
        <button class="btn btn-success" type="submit">
          Sign Up
        </button>
      </>
    );
  } else {
    return (
      <>
        <button class="btn btn-success" type="submit">
          Log Out
        </button>
      </>
    );
  }
};

const NavBar = () => {
  return (
    <nav class="navbar navbar-expand-lg">
      <div class="container-fluid">
        <button
          class="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarSupportedContent"
          aria-controls="navbarSupportedContent"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarSupportedContent">
          <ul class="navbar-nav me-auto mb-2 mb-lg-0">
            <li class="nav-item">
              <a class="nav-link" href="#">
                Company
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="#">
                Product
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="#">
                Pricing
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="#">
                Services
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="#">
                Research
              </a>
            </li>
          </ul>
          <Button />
        </div>
      </div>
    </nav>
  );
};

function App() {
  const [count, setCount] = useState(0);

  return (
    <>
      <NavBar />
      <h2>Nyrkiö</h2>
    </>
  );
}

export default App;
