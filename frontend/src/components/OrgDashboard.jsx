import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { TableOrResult } from "./TableOrResult";
import { dashboardTypes, getOrg } from "../lib/utils";

export const OrgDashboard = ({embed}) => {
  const location = useLocation();
  const [loading, setLoading] = useState(false);
  const [prefix, setPrefix] = useState(undefined);
  const [orgData, setOrgData] = React.useState([]);

  document.body.classList.add("section-dashboards");

  const fetchOrgs = async () => {
    const response = await fetch("/api/v0/orgs/results", {
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    });

    const data = await response.json();
    console.debug(data);
    let results = [];

    data.map((result) => {
      results.push(result.test_name);
    });
    setOrgData(results);
  };

  useEffect(() => {
    setLoading(true);

    var path = location.pathname.substring("/orgs".length);
    if (path.startsWith("/")) {
      path = path.substring(1);
    }

    // The path parsing code relies on using "path === undefined"
    // as a signal that the user is at the root of a dashboard.
    if (path === "") path = undefined;

    setPrefix(path);

    fetchOrgs().finally(() => {
      setLoading(false);
    });
  }, [location]);

  const baseUrls = {
    testRootTitle: "GH Repos",
    api: "/api/v0/orgs/result/",
    apiRoot: "/api/v0/orgs/",
    testRoot: "/orgs",
    results: "/orgs",
    result: "orgs",
    tests: "orgs",
    breadcrumbTestRootTitle: "Github Org",
    resultsWithOrg: "/orgs",
  };

  return (
    <>
      <div className="row text-center">
        <h1 className="mb-4">Organization Test Results</h1>
      </div>
      <div className="row justify-content-center text-center pt-5">
        {loading ? (
          <p>Loading...</p>
        ) : (
          <TableOrResult
            prefix={prefix}
            data={orgData}
            baseUrls={baseUrls}
            dashboardType={dashboardTypes.ORG}
            embed={embed}
            loading={loading}
            setLoading={setLoading}
          />
        )}
      </div>
    </>
  );
};
