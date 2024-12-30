import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Link, useLocation } from "react-router-dom";
import { PropTypes } from "prop-types";
import { DrawLineChart } from "./DrawLineChart";
import { ChangePointSummaryTable } from "./ChangePointSummaryTable";
import { NoMatch } from "./NoMatch";
import { createShortNames, dashboardTypes, applyHash, parseTimestamp } from "../lib/utils";
import { TestSettings } from "./TestSettings";
import { HunterSettings } from "./UserSettings";
import { HunterSettingsOrg } from "./OrgSettings";
import { SidePanel } from "./SidePanel";

import graph_4x4 from "../static/icons/graph-4x4.png";
import graph_nx1 from "../static/icons/graph-nx1.png";
import graph_2x1 from "../static/icons/graph-2x1.png";
import graph_1x1 from "../static/icons/graph-1x1.png";

const isPublicDashboard = (dashboardType) => {
  return dashboardType === dashboardTypes.PUBLIC;
};

const Loading = ({loading}) => {
  if (loading) {
    return (<><div>Loading...</div></>);
  }
  return (<><div className="loading_done"></div></>);
};

export const Breadcrumb = ({ testName, baseUrls }) => {
  const createItems = () => {
    if (testName === undefined) {
      return <></>;
    }

    return testName.split("/").map((name, i) => {
      // Check if we're the last component
      if (i === testName.split("/").length - 1) {
        return (
          <li className="breadcrumb-item active" aria-current="page" key="leaf">
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
      <nav className="navbar col-xs-12 col-lg-11 col-xl-10">
        <div className="container-fluid breadcrumb-wrapper">
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb">
              {console.log(baseUrls.breadCrumbtestRootTitle)}

              {baseUrls.breadcrumbTestRootTitle ? (
                <li className="breadcrumb-item" key="root">
                  <Link to={`${baseUrls.testRoot}`}>
                    {baseUrls.breadcrumbTestRootTitle}
                  </Link>
                </li>
              ) : (
                <span></span>
              )}
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
      <li className="list-group-item nyrkio-empty" key="0">
        <span
          className="bi bi-emoji-surprise"
          title="There are no test results"
        ></span>
      </li>
    );
  }

  return shortNames.map((name, index) => {
    const displayName = displayNames[index];
    var longName = prefix === undefined ? name : prefix + "/" + name;
    if (testNames.includes(longName) || testNames.includes(name)) {
      if (!testNames.includes(longName)) longName = name;
      return (
        <li className="list-group-item" key={longName}>
          <Link
            to={`/${baseUrls.result}/${longName}`}
            state={{ testName: longName }}
          >
            {displayName}
          </Link>
          <SummarizeChangePoints
            name={name}
            longName={longName}
            baseUrls={baseUrls}
            testNames={testNames}
          />
        </li>
      );
    } else {
      var p = name;
      if (prefix !== undefined) p = prefix + "/" + name;
      return (
        <li className="list-group-item" key={longName}>
          <Link to={`/${baseUrls.tests}/${p}`} state={{ testName: name }}>
            <TestListEntry
              name={displayName}
              longName={longName}
              baseUrls={baseUrls}
              testNames={testNames}
            />
          </Link>
        </li>
      );
    }
  });
};

export const Dashboard = ({loggedIn, embed}) => {
  const [loading, setLoading] = useState(false);
  const [unencodedTestNames, setUnencodedTestNames] = useState([]);
  const location = useLocation();
  var prefix;

  document.body.classList.add("section-dashboards");

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
      setUnencodedTestNames((prevState) => [...prevState, test_name]);
    });
    setLoading(false);

  };

  useEffect(() => {
    setLoading(true);
    fetchData();
  }, []);

  const testNames = unencodedTestNames.map((name) => encodeURI(name));

  // Check for invalid test name in url
  if (prefix !== undefined && !validTestName(prefix, testNames)) {
    return <NoMatch />;
  }

  const shortNames = createShortNames(prefix, testNames);
  const displayNames = shortNames.map((name) => decodeURI(name));
  console.log(embed);


  return (
    <>
      {embed == "yes" ? "" :
      <Breadcrumb
        testName={prefix}
        baseUrls={{ tests: "tests", testRoot: "/", testRootTitle: "Tests" }}
      />
    }

      <div className="container-fluid p-5 text-center benchmark-select col-sm-12 col-lg-11 col-xl-10">
            <Loading loading={loading} />
            <div className="container-fluid">
              <div className="card">
                <div className="card-header">Please select a test</div>
                <div className="card-body">
                  <ul className="list-group list-group-flush">
                    <TestList
                      baseUrls={{
                        tests: "tests",
                        result: "result",
                        api: "/api/v0/result/",
                      }}
                      testNames={testNames}
                      shortNames={shortNames}
                      prefix={prefix}
                      displayNames={displayNames}
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
            </div>
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
  dashboardType,
  embed
}) => {
  const [loading, setLoading] = useState(false);
  const [displayData, setDisplayData] = useState([]);
  const [changePointData, setChangePointData] = useState([]);
  const [notFound, setNotFound] = useState(false);
  const [searchParams, setSearchParams] = useSearchParams();
  const numericTimestamp = searchParams.get("timestamp");
  const textTimestamp = parseTimestamp(numericTimestamp);
  console.debug("Display data");
  console.debug(displayData);

  console.debug("Dashboardtype: " + dashboardType);

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
    if (changes.status != 200) {
      console.error("Failed to fetch change point data: " + changes.status);
      return;
    }
    setChangePointData(changeData);
  };

  const [graphSize, setGraphSize] = useState("sparklines");
  const resetOtherButtons = (selectButton) => {
    if (selectButton.id != "btn-graph-overview"){
      document.getElementById("btn-graph-overview").classList.remove("btn-success");
    }
    if (selectButton.id != "btn-graph-sparklines"){
      document.getElementById("btn-graph-sparklines").classList.remove("btn-success");
    }
    if (selectButton.id != "btn-graph-2x1"){
      document.getElementById("btn-graph-2x1").classList.remove("btn-success");
    }
    if (selectButton.id != "btn-graph-1x1"){
      document.getElementById("btn-graph-1x1").classList.remove("btn-success");
    }
    selectButton.classList.add("btn-success");
    // The above doesn't work every time, so schedule backup executions to happen later, to avoid race
    setTimeout(()=>{
      document.getElementById(selectButton.id).classList.add("btn-success");
    },100);
  }
  const setLayout = (e) =>{
      const newLayout = e.currentTarget.id.substring(10);
      console.log(newLayout);
      setGraphSize(newLayout);
      resetOtherButtons(e.currentTarget);
      e.preventDefault();
      e.stopPropagation();
  };
  const GraphSizePicker = () => {
    return (<>
            <div className="card col-md-8">
            <div className="card-header text-center mb-4 mt-3">Choose layout</div>
            </div>
            <div className="card col-md-12">
            <div className="row justify-content-center text-center">
            <a  id="btn-graph-overview" href="#" onClick={(e) => setLayout(e)} className="btn btn-primary col-sm-4 col-lg-2">
            <img src={graph_4x4} alt="4x4" title="Show graphs in a overview layout"  style={{width:100, height:60}} />
            </a>

            <a  id="btn-graph-sparklines" href="#" onClick={(e) => setLayout(e)} className="btn btn-primary col-sm-4  col-lg-2">
            <img src={graph_nx1} alt="nx1" title="Show graphs in a sparkline layout"  style={{width:100, height:60}} />
            </a>
            <a  id="btn-graph-2x1" href="#" onClick={(e) => setLayout(e)} className="btn btn-primary col-sm-4  col-lg-2">
            <img src={graph_2x1} alt="2x1" title="Show 2 large graphs"  style={{width:100, height:60}} />
            </a>
            <a  id="btn-graph-1x1" href="#" onClick={(e) => setLayout(e)} className="btn btn-primary col-sm-4  col-lg-2">
            <img src={graph_1x1} alt="1x1" title="Show 1 graphfor maximum detail" style={{width:100, height:60}} />
            </a>
            {embed == "yes" ? "" :
            <a  href="?embed=yes" className="btn btn-primary col-sm-4  col-lg-2" style={{backgroundColor: "#ffffffff", minWidth:100, minHeight:70}}><span style={{position: "relative", top: "25%", color: "#999999", fontWeight: "bold", border: "2px solid #999999", padding: "10px"}}>Embed</span></a>

            }
            </div>
            </div>
            </>);
  }

  const loadData = () => {
    setLoading(true);
    fetchData().finally(() => {
      setLoading(false);
    });
  };
  useEffect(loadData, []);

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
  console.debug("unique: " + unique);
  applyHash();
  const orgName = testName.split("/")[0];  // Not used when not an org
  return (
    <>
          {embed == "yes" ? "" :
          <Breadcrumb testName={breadcrumbName} baseUrls={baseUrls} />
          }
          <div className="container">
            <Loading loading={loading} />
            <div className="row justify-content-center">
              <ChangePointSummaryTable changeData={changePointData} queryStringTextTimestamp={textTimestamp} />
            </div>

            <div id="graphs" className="row">
            <p style={{textAlign: "right"}}><a href="#graphs" style={{color: "#999999", float: "right"}}>¶</a></p>
            </div>
            <div className="text-end " id="dashboard_settings">
            <button className="btn" title="settings" type="button" id="dashboardSettingsButton" data-bs-toggle="collapse"  data-target="#dashboardSettingsCollapse" href="#dashboardSettingsCollapse" aria-expanded="false" aria-controls="dashboardSettingsCollapse"
            style={{marginBottom: 0}}>
            <span className="bi bi-gear-fill"> </span>
            </button>
            <div className="collapse text-lg-end" aria-labelledby="dashboardSettingsButton" id="dashboardSettingsCollapse">
              <div  className="card card-body">

            <div className="row justify-content-center text-center">
              <GraphSizePicker />
            </div>

            <div className="row justify-content-center text-center hunter-settings">
            {dashboardType == dashboardTypes.ORG ?
              <HunterSettingsOrg orgName={orgName} callback={loadData}/> :
              <HunterSettings callback={loadData}/>
            }
            </div>

            {!isPublicDashboard(dashboardType) && (
                <div className="row justify-content-center text-center">
                <div className="card col-md-8">
                <div className="card-header justify-content-center text-center mb-3 mt-5">Publish test results</div>
                <TestSettings
                  dashboardType={dashboardType}
                  testName={testName}
                  attributes={
                    displayData.length > 0
                      ? displayData[displayData.length - 1].attributes
                      : undefined
                  }
                />
              </div>
              </div>
            )}
              </div>
            </div>
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
                    key={testName+"/"+metric.name}
                    searchParams={searchParams}
                    graphSize={graphSize}
                  />
                );
              })}
            </div>
          </div>
    </>
  );
};

SingleResultWithTestname.propTypes = {
  testName: PropTypes.string.isRequired,
};

export const SingleResult = ({embed}) => {
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
      dashboardType={dashboardTypes.USER}
      embed={embed}
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
const TestListEntry = ({ name, longName, baseUrls, testNames }) => {
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
    return (
      <>
        <div className="row justify-content-center">
          <div className="col">
            {name}{" "}
            <SummarizeChangePoints
              name={name}
              longName={longName}
              baseUrls={baseUrls}
              testNames={testNames}
            />
          </div>
        </div>
      </>
    );
  }

  if (imageUrl) {
    return (
      <div className="row justify-content-center">
        <Loading loading={loading} />
        <div className="col-1">
          <img
            src={imageUrl}
            alt="GitHub repo avatar"
            title="GitHub repo avatar"
            style={{ width: "30px", height: "30px" }}
          />
        </div>
        <div className="col">
          {name}{" "}
          <SummarizeChangePoints
            name={name}
            longName={longName}
            baseUrls={baseUrls}
            testNames={testNames}
          />
        </div>
      </div>
    );
  } else {
    return (
      <>
        <div className="row justify-content-center">
          <Loading loading={loading} />
          <div className="col">
            {name}{" "}
            <SummarizeChangePoints
              name={name}
              longName={longName}
              baseUrls={baseUrls}
              testNames={testNames}
            />
          </div>
        </div>
      </>
    );
  }
};

// Helper function to catch invalid urls that contain non-existent test names
const validTestName = (name, testNames) => {
  const match = testNames.filter((test) => test.startsWith(name));
  return match.length > 0;
};

const SummarizeChangePoints = ({ longName, baseUrls, testNames }) => {
  const [rawChanges, setRawChanges] = useState({});
  const [sumChanges, setSumChanges] = useState(0);
  const [firstChanges, setFirstChanges] = useState("");

  const fetchSummaryApi = async (prefix) => {
    console.debug("Fetching summary for " + prefix);
    const url = baseUrls.api + prefix + "/summary";
    const response = await fetch(url, {
      headers: {
        "Content-type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    });

    if (response.status != 200) {
      console.error("Failed to fetch summary: " + response.status);
      return;
    }

    const resultData = await response.json();
    setRawChanges(resultData);
  };

  useEffect(() => {
    //const res = fetchSummarizedData(longName);
    const res = fetchSummaryApi(longName);

    return () => {
      const a = 1;
      //console.log(rawChanges);
    };
  }, [baseUrls, longName, testNames]);

  useEffect(() => {
    var newestDate = new Date();
    console.debug(longName);
    console.debug(rawChanges);
    if (
      rawChanges.total_change_points &&
      parseInt(rawChanges.total_change_points)
    ) {
      setSumChanges(rawChanges["total_change_points"]);
    }
    if (rawChanges.newest_time && parseInt(rawChanges.newest_time)) {
      newestDate = new Date(1000 * parseInt(rawChanges["newest_time"]));
      setFirstChanges(newestDate.toLocaleString());
    }
  }, [rawChanges]);

  //   console.debug(sumChanges);
  //   console.debug(firstChanges);
  if (sumChanges > 0 && firstChanges)
    return (
      <>
        <div
          className="summarize-change-points"
          style={{
            position: "absolute",
            right: "0.5em",
            top: 0,
            textAlign: "right",
          }}
        >
          <span className="summarize-cp-sum-total">
            {sumChanges > 0 ? sumChanges : ""}
          </span>
          <span className="summarize-cp-text summarize-cp-text-changes">
            &nbsp;changes,
          </span>
          <br />
          <span className="summarize-cp-text summarize-cp-text-latest">
            latest on&nbsp;
          </span>
          <span className="summarize-cp-first-changes">{firstChanges}</span>
        </div>
      </>
    );
  else return <span className="summarize-cp-no-changes"></span>;
};
