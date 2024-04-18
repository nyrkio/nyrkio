import React, { useState } from "react";
import { Link } from "react-router-dom";

export const SidePanel = () => {
  const [content, setContent] = useState("");

  return (
    <div className="navbar-nav navbar-left justify-content-start col-sm-3 pe-1 p-1">
      {/*<div class="col-auto col-md-3 col-xl-2 px-sm-2 px-0">*/}
      <Link to="/" className="nav-link">
        My Dashboard
      </Link>
      <Link to="/orgs" className="nav-link">
        Org Dashboards
      </Link>
      <Link to="/public" className="nav-link">
        Public Dashboards
      </Link>
    </div>
  );
};
