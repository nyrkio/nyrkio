import "bootstrap-icons/font/bootstrap-icons.css";
import Dropdown from "react-bootstrap/Dropdown";
import { Link } from "react-router-dom";

export const UserMenu = ({ setLoggedIn }) => {
  const handleLogoutClick = () => {
    console.log("Setting logged in to false");
    setLoggedIn(false);
    localStorage.setItem("loggedIn", "false");
  };
  return (
    <Dropdown>
      <Dropdown.Toggle variant="success" id="dropdown-basic">
        <b className="bi bi-gear-fill"></b>
      </Dropdown.Toggle>

      <Dropdown.Menu>
        <Dropdown.Item href="/user/settings">
          <Link to="/user/settings">
            <span className="bi bi-person-circle"></span> User Settings
          </Link>
        </Dropdown.Item>

        <Dropdown.Divider />

        <Dropdown.Item href="/" onClick={handleLogoutClick}>
          <Link to="/">
            <span className="bi bi-box-arrow-right"></span> Log Out
          </Link>
        </Dropdown.Item>
      </Dropdown.Menu>
    </Dropdown>
  );
};
