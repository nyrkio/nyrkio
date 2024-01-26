import { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import "./App.css";
import { Login } from "./components/Login.jsx";
import { Dashboard, SingleResult } from "./components/Dashboard.jsx";
import { FrontPage } from "./components/FrontPage.jsx";
import { NavHeader } from "./components/Nav.jsx";
import { ProductPage } from "./components/ProductPage.jsx";

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
  const [loggedIn, setLoggedIn] = useState(() => {
    const saved = localStorage.getItem("loggedIn");
    const initialValue = JSON.parse(saved);
    return initialValue || false;
  });

  return (
    <>
      <Router>
        <NavHeader loggedIn={loggedIn} setLoggedIn={setLoggedIn} />
        <Routes>
          <Route path="/" element={<Root loggedIn={loggedIn} />} />
          <Route path="/product" element={<ProductPage />} />
          <Route
            path="/login"
            element={<Login loggedIn={loggedIn} setLoggedIn={setLoggedIn} />}
          />
          <Route path="/result/:testName" element={<SingleResult />} />
          <Route path="*" element={<NoMatch />} />
        </Routes>
      </Router>
    </>
  );
}

export default App;
