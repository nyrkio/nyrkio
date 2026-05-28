import React, { useState, useEffect } from "react";
import { Routes, Route, Link, NavLink } from "react-router-dom";

export const SidePanel = ({ loggedIn }) => {
  const [orgs, setOrgs] = useState([]);
  const getOrganizations = async () => {
    if (!loggedIn){
      return;
    }
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


  return (
    <div className="nav nav-pills nav-pills--sidebar rounded-2 shadow-sm d-inline-flex mx-auto column-gap-4 justify-content-center w-100 w-md-auto">
      <Routes>
        <Route path="/" element={<FrontPageSidePanel loggedIn={loggedIn} />} />
        <Route path="/dash" element={<DashSidePanel loggedIn={loggedIn} />} />

        <Route
          path="/frontpage"
          element={<FrontPageSidePanel loggedIn={loggedIn} />}
        />
        <Route
          path="/tests/*"
          element={<DashSidePanel loggedIn={loggedIn} />}
        />
        <Route
          path="/result/*"
          element={<DashSidePanel loggedIn={loggedIn} />}
        />
        <Route
          path="/public/*"
          element={<DashSidePanel loggedIn={loggedIn} />}
        />
        <Route
          path="/orgs/*"
          element={<DashSidePanel loggedIn={loggedIn} />}
        />

        <Route
          path="/product"
          element={<ProductSidePanel loggedIn={loggedIn} />}
        />
        <Route
          path="/product/*"
          element={<ProductSidePanel loggedIn={loggedIn} />}
        />
        <Route path="/docs/*" element={<DocsSidePanel loggedIn={loggedIn} />} />
        <Route
          path="/legend"
          element={<AboutSidePanel loggedIn={loggedIn} />}
        />
        <Route
          path="/about/*"
          element={<AboutSidePanel loggedIn={loggedIn} />}
        />
        <Route
          path="/legal/*"
          element={<AboutSidePanel loggedIn={loggedIn} />}
        />
        <Route
          path="/signup"
          element={<LoginSidePanel loggedIn={loggedIn} />}
        />
        <Route path="/login" element={<LoginSidePanel loggedIn={loggedIn} />} />
        <Route path="/billing" element={<SettingsSidePanel loggedIn={loggedIn} orgs={orgs}/>} />
        <Route path="/user/settings" element={<SettingsSidePanel loggedIn={loggedIn} orgs={orgs}/>} />
        <Route path="/org/*" element={<SettingsSidePanel loggedIn={loggedIn} orgs={orgs}/>} />
        </Routes>
    </div>
  );
};

const FrontPageSidePanel = ({ loggedIn }) => {
  if (loggedIn) {
    return (
      <>
      </>
    );
  }
  // The default front page has no menu for visual reasons.
  // Login button is on the top right, which is the most important element.
  else {
    return <></>;
  }
};

const DashSidePanel = ({ loggedIn }) => {
  document.body.classList.add("section-dash");
  if (loggedIn) {
    return (
      <>
      <Link to="/tests" className="nav-link">
      My Dashboard
      </Link>
      <Link to="/orgs" className="nav-link">
      Org Dashboards
      </Link>
      <Link to="/public" className="nav-link">
      Public Dashboards
      </Link>
      <Link to="/frontpage" className="nav-link">
      Front page
      </Link>
      </>
    );
  }
  // The default front page has no menu for visual reasons.
  // Login button is on the top right, which is the most important element.
  else {
    return (<>
    <Link to="/docs/getting-started" className="nav-link">
    Create My Dashboard
    </Link>
    <Link to="/public" className="nav-link">
    Public Dashboards
    </Link>
    <Link to="/frontpage" className="nav-link">
    Front page
    </Link>
    </>
    );
  }
};

const ProductSidePanel = ({ loggedIn }) => {
  document.body.classList.add("section-product");
  return (
    <>
      <NavLink to="/product" end className="nav-link">Nyrkiö Change Detection</NavLink>
      <NavLink to="/product/user-testimonials" className="nav-link">What our users say</NavLink>
      {loggedIn ?
        <NavLink to="/billing" className="nav-link">
        Billing
        </NavLink>
        :
        ""
      }
    </>
  );
};

const DocsSidePanel = ({ loggedIn }) => {
  document.body.classList.add("section-docs");

  return (
    <>
      <NavLink to="/docs/getting-started" className="nav-link">Nyrkio Runners</NavLink>
      <NavLink to="/docs/change-detection" className="nav-link">Change Detection</NavLink>
      <NavLink to="/docs/getting-started-http" className="nav-link">HTTP API</NavLink>
      <NavLink to="/docs/working-with-graphs" className="nav-link">Working with the graphs</NavLink>
      <NavLink to="/docs/git-perf-plugin" className="nav-link">git-perf plugin</NavLink>
      <NavLink to="/docs/teams" className="nav-link">Teams / Orgs</NavLink>
      <a className="nav-link" href="/openapi">API</a>
    </>
  );
};
const AboutSidePanel = ({ loggedIn }) => {
  document.body.classList.add("section-about");
  return (
    <>
      <NavLink to="/about" end className="nav-link">
        About Nyrkiö Oy
      </NavLink>
      <NavLink to="/about/ecosystem" className="nav-link">
      Open Source Ecosystem
      </NavLink>
      <NavLink to="/legal" className="nav-link">
      Legal
      </NavLink>
      <NavLink to="/legend" className="nav-link">
        The Legend of Nyyrikki
      </NavLink>
    </>
  );
};
const LoginSidePanel = ({ loggedIn }) => {
  document.body.classList.add("section-login");
  // The links are present in the header and at the bottom of the login/register forms.
  return (
    <>
    </>
  );
};

const SettingsSidePanel = ({ loggedIn, orgs }) => {
  document.body.classList.add("section-settings");
  return (
    <>
    <Link to="/user/settings" className="nav-link nav-link-login">
    <span className="bi bi-person-fill"></span> User Settings
    </Link>
    <OrgsList orgs={orgs}/>
    <Link to="/billing" className="nav-link nav-link-login">
    <span className="bi bi-credit-card"></span> Billing
    </Link>
    <Link to="/pricing" className="nav-link nav-link-login">
    <span className="bi bi-credit-card"></span> Upgrade your subscription
    </Link>
    </>
  );
};
const OrgsList = ({orgs}) => {
  const orgsHtml = [];
  for (let i=0; i<orgs.length; i++){
    const thisOrg = orgs[i];
    orgsHtml.push(
      <Link to={"/org/"+thisOrg}  className="nav-link nav-link-login" key={i}>
      <span className="bi bi-people-fill"></span> {thisOrg} Settings
      </Link>
    );
  }
  return (<>{orgsHtml}</>);
};
