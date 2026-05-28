import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import "bootstrap-icons/font/bootstrap-icons.css";
import Dropdown from "react-bootstrap/Dropdown";
import { ImpersonateControls } from "./ImpersonateControls";
import posthog from "posthog-js";

export const UserMenu = ({ loggedIn, setLoggedIn }) => {
  const [isAdmin, setIsAdmin] = useState(false);
  const [orgs, setOrgs] = useState([]);
  var username = null;
  if (loggedIn) {
    username = localStorage.getItem("username");
  }

  const navigate = useNavigate();


  const checkForAdminPrvis = async () => {
    const response = await fetch("/api/v0/auth/admin", {
      method: "GET",
      credentials: "include",
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
      credentials: "include",
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
      if ( data !== undefined && data.forEach ){
        data.forEach((d) => {
          temp.push(d.organization.login);
        });
      }
      setOrgs(temp);
    } );
  }, []);

  const handleLogoutClick = async () => {
    const response = await fetch("/api/v0/auth/cookie/logout", {
      method: "POST",
      credentials: "include",
    });
    if (response.status !== 200 && response.status !== 204) {
      console.error(
        "Failed to log out: " + response.status + " " + response.statusText,
      );
    }
    console.log("Setting logged in to false");
    setLoggedIn(false);

    localStorage.removeItem("token");
    localStorage.setItem("username", "");
    localStorage.setItem("username_real", "");
    document.body.classList.remove( "impersonate-user" );

    posthog.reset();

    try {
      navigate("/");
    } catch (error) {
      console.log(error);
    }

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
    <Dropdown id="dropdownwrapper">
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

        <Dropdown.Item href="/forgot-password">
          <span className="bi bi-filetype-sh"></span> Change Password
        </Dropdown.Item>

        <Dropdown.Item onClick={handleLogoutClick}>
          <span className="bi bi-box-arrow-right"></span> Log Out
        </Dropdown.Item>
      </Dropdown.Menu>
    </Dropdown>
  );
};
