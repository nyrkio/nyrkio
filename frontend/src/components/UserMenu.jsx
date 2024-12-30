import { useState, useEffect } from "react";
import "bootstrap-icons/font/bootstrap-icons.css";
import Dropdown from "react-bootstrap/Dropdown";
import { ImpersonateControls } from "./ImpersonateControls";

export const UserMenu = ({ setLoggedIn }) => {
  const [isAdmin, setIsAdmin] = useState(false);
  const [orgs, setOrgs] = useState([]);
  var username = null;
  if (localStorage.getItem("loggedIn") == "true") {
    username = localStorage.getItem("username");
  }
  console.debug("username");
  console.debug(username);
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
  const getOrganizations = async () => {
    const url = "/api/v0/orgs/";
    console.debug("GET " + url);
    const response = await fetch(url, {
      headers: {
        "Content-type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    });

    if (response.status !== 200) {
      console.error("Failed to GET User's organizations");
      console.log(response);
      return response;
    } else console.debug(response);

    const data = await response.json();
    console.debug(data);
    if ( Array.isArray(data)  ) {
      return data;
    } else {
      return ["Fetching your organizations failed."];
    }
  };

  useEffect(() => {
    checkForAdminPrvis();
    getOrganizations().then((data) => {

      var temp = [];
      if ( data !== undefined ){
        data.forEach((d) => {
          temp.push(d.organization.login);
        });
      }
      setOrgs(temp);
    } );
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
        "Failed to log out: " + response.status + " " + response.statusText,
      );
    }
    setLoggedIn(false);
    localStorage.setItem("loggedIn", "false");
    localStorage.removeItem("token");
  };

  const orgsList = () => {
    const orgsHtml = [];
    for (let i=0; i<orgs.length; i++){
      const thisOrg = orgs[i];
      orgsHtml.push(
          <Dropdown.Item href={"/org/"+thisOrg} key={i}>
            <span className="bi bi-people-fill"></span> {thisOrg} Settings
          </Dropdown.Item>
      );
    }
    return orgsHtml;
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
          <span className="bi bi-person-fill"></span> User Settings
        </Dropdown.Item>

        {orgsList()}

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
