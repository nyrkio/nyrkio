import { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import "./App.css";
import { Login } from "./components/Login.jsx";
import { Dashboard, SingleResult } from "./components/Dashboard.jsx";
import { FrontPage } from "./components/FrontPage.jsx";
import { NavHeader } from "./components/Nav.jsx";

function NoMatch() {
  return (
    <div style={{ padding: 20 }}>
      <h2>404: Page Not Found</h2>
      <p>Lorem ipsum dolor sit amet, consectetur adip.</p>
    </div>
  );
}

const Root = ({ loggedIn }) => {
  return (
    <>
      <div className="container mt-5 text-center">
        {loggedIn ? <Dashboard /> : <FrontPage />}
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
