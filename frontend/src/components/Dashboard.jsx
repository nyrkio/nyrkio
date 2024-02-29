import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { PropTypes } from "prop-types";
import { DrawLineChart } from "./DrawLineChart";
import { ChangePointSummaryTable } from "./ChangePointSummaryTable";
import { NoMatch } from "./NoMatch";
import { createShortNames } from "../lib/utils";
import { TestSettings } from "./TestSettings";

export const Breadcrumb = ({ testName, baseUrls }) => {
  const createItems = () => {
    if (testName === undefined) {
      return <></>;
    }

    return testName.split("/").map((name, i) => {
      // Check if we're the last component
      if (i === testName.split("/").length - 1) {
        return (
          <li className="breadcrumb-item active" aria-current="page" key={i}>
            {decodeURIComponent(name)}
          </li>
        );
      }

      var prefix = testName
        .split("/")
        .slice(0, i + 1)
        .join("/");
      return (
        <li className="breadcrumb-item" key={prefix}>
          <Link to={`/${baseUrls.tests}/${prefix}`}>
            {decodeURIComponent(name)}
          </Link>
        </li>
      );
    });
  };

  console.debug("baseUrls: " + baseUrls.testRoot);

  return (
    <>
      <nav className="navbar navbar-expand-lg">
        <div className="container-fluid breadcrumb-wrapper">
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb">
              <li className="breadcrumb-item" key="root">
                <Link to={`${baseUrls.testRoot}`}>
                  {baseUrls.testRootTitle}
                </Link>
              </li>
              {createItems()}
            </ol>
          </nav>
        </div>
      </nav>
    </>
  );
};

export const TestList = ({
  baseUrls,
  testNames,
  shortNames,
  displayNames,
  prefix,
}) => {
  if (shortNames.length == 0) {
    return (
      <li className="list-group-item nyrkio-empty">
        <span
          className="bi bi-emoji-surprise"
          title="There are no test results"
        ></span>
      </li>
    );
  }

  return shortNames.map((name, index) => {
    const displayName = displayNames[index];
    var longName = prefix + "/" + name;
    if (testNames.includes(longName) || testNames.includes(name)) {
      if (!testNames.includes(longName)) longName = name;
      return (
        <li className="list-group-item">
          <Link
            to={`/${baseUrls.result}/${longName}`}
            state={{ testName: longName }}
          >
            {name}
          </Link>
        </li>
      );
    } else {
      var p = name;
      if (prefix !== undefined) p = prefix + "/" + name;
      return (
        <li className="list-group-item">
          <Link to={`/${baseUrls.tests}/${p}`} state={{ testName: name }}>
            <TestListEntry name={displayName} />
          </Link>
        </li>
      );
    }
  });
};

export const Dashboard = () => {
  const [loading, setLoading] = useState(false);
  const [testNames, setTestNames] = useState([]);
  const location = useLocation();
  var prefix;

  // Remove /tests/ from the beginning of the path
  if (location.pathname.startsWith("/tests/")) {
    prefix = location.pathname.substring(7);

    // Strip trailing / if it exists
    if (prefix.endsWith("/")) {
      prefix = prefix.substring(0, prefix.length - 1);
    }

    // If the prefix is empty, set it to undefined
    if (prefix === "") {
      prefix = undefined;
    }
  }

  const fetchData = async () => {
    const response = await fetch("/api/v0/results", {
      headers: {
        "Content-type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    });

    if (response.status != 200) {
      console.error("Failed to fetch test names: " + response.status);
      return;
    }

    const resultData = await response.json();
    resultData.map((element) => {
      const test_name = element.test_name;
      setTestNames((prevState) => [...prevState, test_name]);
    });
    setLoading(false);
  };

  useEffect(() => {
    setLoading(true);
    fetchData();
  }, []);

  if (loading) {
    return <div>Loading</div>;
  }

  // Check for invalid test name in url
  if (prefix !== undefined && !validTestName(prefix, testNames)) {
    return <NoMatch />;
  }

  const shortNames = createShortNames(prefix, testNames);

  return (
    <>
      <Breadcrumb
        testName={prefix}
        baseUrls={{ tests: "tests", testRoot: "/", testRootTitle: "Tests" }}
      />
      <div className="container mt-5 text-center benchmark-select">
        {loading ? (
          <div>Loading</div>
        ) : (
          <>
            <div className="container col-10">
              <div className="card">
                <div className="card-header">Please select a test</div>
                <div className="card-body">
                  <ul className="list-group list-group-flush">
                    <TestList
                      baseUrls={{ tests: "tests", result: "result" }}
                      testNames={testNames}
                      shortNames={shortNames}
                      prefix={prefix}
                      displayNames={shortNames}
                    />
                  </ul>
                </div>
              </div>

              <div className="card">
                <div className="card-body create-new-test">
                  <Link to="/docs/getting-started" className="btn btn-success">
                    <span className="bi bi-plus-square-fill">
                      &nbsp;&nbsp; Add test results
                    </span>
                  </Link>
                </div>
              </div>

              <div className="card">
                <div className="card-body">
                &nbsp;
                 </div>
              </div>

              <div className="card">
                <div className="card-header">Public Test Results</div>
                <div className="card-body">
                  <a href="/public">
                    Public Test Results
                  </a>
                </div>
              </div>


            </div>
          </>
        )}
      </div>
    </>
  );
};

// This component is used to display the results of a single test. testName is
// the name of the test as used by the API.
//
// breadcrumbName is the name of the test as displayed in the breadcrumb
// component. Most of the time this is the same as testName but the public dashboard
// uses a URL-decoded version of the name.
//
// isPublicDashboard is used to show/hide the "Make public" switch since it's only
// available if the user is editing their own tests.
export const SingleResultWithTestname = ({
  testName,
  baseUrls,
  breadcrumbName,
  isPublicDashboard,
}) => {
  const [loading, setLoading] = useState(false);
  const [displayData, setDisplayData] = useState([]);
  const [changePointData, setChangePointData] = useState([]);
  const [notFound, setNotFound] = useState(false);
  console.log("Display data");
  console.log(displayData);

  const fetchData = async () => {
    console.debug("Fetching data for " + testName);
    const response = await fetch(baseUrls.api + testName, {
      headers: {
        "Content-type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    });
    if (response.status != 200) {
      setNotFound(true);
      return;
    }
    const resultData = await response.json();
    setDisplayData(resultData);

    const changes = await fetch(baseUrls.api + testName + "/changes", {
      headers: {
        "Content-type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    });
    const changeData = await changes.json();
    setChangePointData(changeData);
  };

  useEffect(() => {
    setLoading(true);
    fetchData().finally(() => {
      setLoading(false);
    });
  }, []);

  if (notFound) {
    return <NoMatch />;
  }

  const timestamps = displayData.map((result) => {
    return result.timestamp;
  });

  var metricMap = [];
  displayData.map((result) => {
    result.metrics.map((metric) => {
      metricMap.push({ name: metric.name, unit: metric.unit });
    });
  });

  // Only want unique metric names
  var unique = metricMap.reduce((a, b) => {
    if (a.findIndex((x) => x.name === b.name) === -1) {
      return a.concat([b]);
    } else {
      return a;
    }
  }, []);
  console.log("unique: " + unique);

  return (
    <>
      {loading ? (
        <div>Loading</div>
      ) : (
        <>
          {!isPublicDashboard && (
            <div className="row">
              <TestSettings
                testName={testName}
                attributes={
                  displayData.length > 0
                    ? displayData[displayData.length - 1].attributes
                    : undefined
                }
              />
            </div>
          )}
          <Breadcrumb testName={breadcrumbName} baseUrls={baseUrls} />
          <div className="container">
            <div className="row justify-content-center">
              <ChangePointSummaryTable changeData={changePointData} />
            </div>
            <div className="row">
              {unique.map((metric) => {
                return (
                  <DrawLineChart
                    changePointData={changePointData}
                    metric={metric}
                    testName={testName}
                    timestamps={timestamps}
                    displayData={displayData}
                  />
                );
              })}
            </div>
          </div>
        </>
      )}
    </>
  );
};

SingleResultWithTestname.propTypes = {
  testName: PropTypes.string.isRequired,
};

export const SingleResult = () => {
  const location = useLocation();

  const testName = location.pathname.substring(8);
  console.log(testName);
  const baseUrls = {
    api: "/api/v0/result/",
    tests: "tests",
    testRoot: "/",
    testRootTitle: "Tests",
  };
  return (
    <SingleResultWithTestname
      testName={testName}
      baseUrls={baseUrls}
      breadcrumbName={testName}
      isPublicDashboard={false}
    />
  );
};

const nameIsGitHubRepo = (name) => {
  return name.toLowerCase().startsWith("https://github.com/");
};

// Create a test list entry element. If the name for this entry
// looks like a GitHub repo, fetch the avatar URL and display it
// alongside the name.
//
// TODO(mfleming) Fetching the avatar url is a really quick way
// to exhaust the GitHub API rate limit. We should cache these.
const TestListEntry = ({ name }) => {
  const [loading, setLoading] = useState(false);
  const [imageUrl, setImageUrl] = useState(undefined);
  const [isGitHubUrl, setIsGitHubUrl] = useState(false);

  const fetchImage = async (repo) => {
    const response = await fetch(`https://api.github.com/repos/${repo}`);
    if (response.status !== 200) {
      console.error("Failed to fetch GitHub repo data: " + response.status);
      return;
    }

    const data = await response.json();
    if (data.owner.avatar_url) {
      setImageUrl(data.owner.avatar_url);
    }
  };

  useEffect(() => {
    if (nameIsGitHubRepo(name)) {
      setIsGitHubUrl(true);
      const url = name;
      const repo = url.replace("https://github.com/", "");
      setLoading(true);
      fetchImage(repo).finally(() => {
        setLoading(false);
      });
    }
  }, []);

  if (!isGitHubUrl) {
    return <>{name}</>;
  }

  if (loading) {
    return <div>Loading</div>;
  }

  if (imageUrl) {
    return (
      <div className="row justify-content-center">
        <div className="col-1">
          <img
            src={imageUrl}
            alt="GitHub repo avatar"
            title="GitHub repo avatar"
            style={{ width: "30px", height: "30px" }}
          />
        </div>
        <div className="col">{name}</div>
      </div>
    );
  } else {
    return <>{name}</>;
  }
};

// Helper function to catch invalid urls that contain non-existent test names
const validTestName = (name, testNames) => {
  const match = testNames.filter((test) => test.startsWith(name));
  return match.length > 0;
};
