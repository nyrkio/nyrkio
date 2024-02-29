import React, { useEffect, useState } from "react";
import { useLocation } from "react-router";
import { TestList, Breadcrumb, SingleResultWithTestname } from "./Dashboard";
import { createShortNames, parseGitHubRepo } from "../lib/utils";

// Decide whether we should display a table of test names or a single result.
// If the current url includes a pathname that we match exactly in publicData
// then we should display that result.
//
// Otherwise, treat the pathname as a prefix for a name in publicData and list
// all tests with that prefix upto the next "/".
const TableOrResult = ({ prefix, publicData }) => {
  const testNames = publicData;
  const shortNames = createShortNames(prefix, testNames);

  const baseUrls = {
    testRootTitle: "GH Repos",
    api: "/api/v0/public/result/",
    testRoot: "/public",
    results: "/public",
    tests: "public",
  };

  // If we found an exact match, display the result
  if (publicData.includes(prefix)) {
    var path = decodeURIComponent(prefix).replace("https://github.com/", "");

    return (
      <>
        <SingleResultWithTestname
          testName={path}
          baseUrls={baseUrls}
          breadcrumbName={prefix}
          isPublicDashboard={true}
        />
      </>
    );
  } else {
    console.debug("publicData: " + publicData);
    // Otherwise, display a list of tests upto the next "/"
    return (
      <>
        <Breadcrumb
          testName={prefix}
          baseUrls={{
            tests: "public",
            testRoot: "/public",
            testRootTitle: "GitHub Repos",
          }}
        />
        <div className="col-md-7">
          <TestList
            baseUrls={{ tests: "public", result: "public" }}
            testNames={publicData}
            shortNames={shortNames}
            displayNames={shortNames.map((name) => decodeURIComponent(name))}
            prefix={prefix}
          />
        </div>
      </>
    );
  }
};

export const PublicDashboard = () => {
  const location = useLocation();
  const [loading, setLoading] = useState(false);
  const [prefix, setPrefix] = useState(undefined);
  const [publicData, setPublicData] = React.useState([]);

  const fetchPublicTests = async () => {
    const response = await fetch("/api/v0/public/results");
    const publicData = await response.json();
    console.debug(publicData);

    let results = [];
    publicData.map((result) => {
      const url = parseGitHubRepo(result);
      console.debug("url: " + url);
      results.push(url);
    });
    setPublicData(results);
  };

  useEffect(() => {
    setLoading(true);

    var path = location.pathname.substring("/public".length);
    if (path.startsWith("/")) {
      path = path.substring(1);
    }

    // The path parsing code relies on using "path === undefined"
    // as a signal that the user is at the root of a dashboard.
    if (path === "") path = undefined;

    setPrefix(path);

    fetchPublicTests().finally(() => {
      setLoading(false);
    });
  }, [location]);

  return (
    <div className="container">
      <div className="row text-center">
        <h1 className="mb-4">Public Test Results</h1>
        <p>Public benchmark results as shared by Nyrkiö users.</p>
      </div>
      <div className="row justify-content-center text-center pt-5">
        {loading ? (
          <p>Loading...</p>
        ) : (
          <TableOrResult prefix={prefix} publicData={publicData} />
        )}
      </div>
    </div>
  );
};
