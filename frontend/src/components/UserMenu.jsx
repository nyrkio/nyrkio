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
        <b class="bi bi-gear"></b>
      </Dropdown.Toggle>

      <Dropdown.Menu>
        <Dropdown.Item href="/" onClick={handleLogoutClick}>
          <Link to="/">
            <i class="bi bi-box-arrow-right"></i> Log Out
          </Link>
        </Dropdown.Item>
      </Dropdown.Menu>
    </Dropdown>
  );
};
