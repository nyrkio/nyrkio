import { useState, useEffect } from "react";
import "bootstrap-icons/font/bootstrap-icons.css";
import Dropdown from "react-bootstrap/Dropdown";

export const UserMenu = ({ setLoggedIn }) => {
  const [isAdmin, setIsAdmin] = useState(false);
  var username = null;
  if (localStorage.getItem("loggedIn") == "true") {
    username = localStorage.getItem("username");
  }

  const checkForAdminPrvis = async () => {
    const response = await fetch("/api/v0/auth/admin", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    });

    if (response.status === 200) {
      setIsAdmin(true);
      localStorage.setItem("admin", "true");
    }
  };

  useEffect(() => {
    checkForAdminPrvis();
  }, []);

  const handleLogoutClick = async () => {
    console.debug("Setting logged in to false");
    const response = await fetch("/api/v0/auth/jwt/logout", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    });
    if (response.status !== 200 && response.status !== 204) {
      console.error(
        "Failed to log out: " + response.status + " " + response.statusText
      );
    }
    setLoggedIn(false);
    localStorage.setItem("loggedIn", "false");
    localStorage.removeItem("token");
  };
  return (
    <Dropdown>
      <Dropdown.Toggle variant="success" id="dropdown-basic">
        <span className="bi bi-gear-fill"> {username}</span>
      </Dropdown.Toggle>

      <Dropdown.Menu>
        {isAdmin ? (
          <Dropdown.Item href="/admin">
            <span className="bi bi-box-arrow-up-right"></span> Admin
          </Dropdown.Item>
        ) : (
          <></>
        )}
        <Dropdown.Item href="/user/settings">
          <span className="bi bi-person-circle"></span> User Settings
        </Dropdown.Item>

        <Dropdown.Item href="/billing">
          <span className="bi bi-credit-card"></span> Billing
        </Dropdown.Item>
        <Dropdown.Divider />

        <Dropdown.Item onClick={handleLogoutClick}>
          <span className="bi bi-box-arrow-right"></span> Log Out
        </Dropdown.Item>
      </Dropdown.Menu>
    </Dropdown>
  );
};
