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
            <i className="bi bi-person-circle"></i> User Settings
          </Link>
        </Dropdown.Item>

        <Dropdown.Divider />

        <Dropdown.Item href="/" onClick={handleLogoutClick}>
          <Link to="/">
            <i className="bi bi-box-arrow-right"></i> Log Out
          </Link>
        </Dropdown.Item>
      </Dropdown.Menu>
    </Dropdown>
  );
};
