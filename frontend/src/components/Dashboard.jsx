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
import { OrgDashboard } from "./OrgDashboard";
import { PublicDashboard } from "./PublicDashboard";
import { TableOrResult } from "./TableOrResult";
import { Breadcrumb } from "./Breadcrumb";

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


export const TestList = ({
  baseUrls,
  testNames,
  shortNames,
  displayNames,
  prefix,
  summaries,setSummaries,
  loading,
  setLoading,
  encodedGhNames,
}) => {
  // Check for invalid test name in url
  if (!loading && prefix !== undefined && !validTestName(prefix, testNames)) {
      return <NoMatch />;
  }
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
    if(summaries&&summaries[longName]){
      summaries[longName].placeholderKey = index;
    }
    if (testNames.includes(longName) || testNames.includes(name)) {
      if (!testNames.includes(longName)) longName = name;
      return (
        <li className="list-group-item" key={index}>
          <Link
            to={`/${baseUrls.result}/${longName}`}
            state={{ testName: longName }}
          >
            {displayName}
          </Link>
          <SummarizeChangePoints
            longName={longName}
            summaries={summaries} loading={loading}
            />
        </li>
      );
    } else {
      var p = name;
      if (prefix !== undefined) p = prefix + "/" + name;
      return (
        <li className="list-group-item" key={index}>
          <Link to={`/${baseUrls.tests}/${p}`} state={{ testName: name }}>
            <TestListEntry
              name={displayName}
              longName={longName}
              baseUrls={baseUrls}
              testNames={testNames}
              summaries={summaries}
              setSummaries={setSummaries}
              setLoading={setLoading}
              loading={loading}
            />
          </Link>
        </li>
      );
    }
  });
};

var summaries2={};
const setSummaries2  = (v)=>{summaries2=v;};
export const Dashboard = ({loggedIn, embed, path}) => {
  document.body.classList.add("section-dashboards");

  if (path=="/result/") return (<MyDashboard loggedIn={loggedIn} embed={embed} path={path} />);
  if (path=="/public/") return PublicDashboard({loggedIn,embed,path});
  if (path=="/orgs/") return OrgDashboard({loggedIn,embed,path});

  if (path=="/tests/"|| path=="/") return (<MyDashboard loggedIn={loggedIn} embed={embed} path={path} />);
  return <NoMatch />;
};

const MyDashboard = ({loggedIn, embed, path}) => {
  const [loading, setLoading] = useState(true);
  const [unencodedTestNames, setUnencodedTestNames] = useState([]);
//   const [summaries, setSummaries] = useState({});
  const location = useLocation();
  var prefix;
  var testName=undefined;

  const baseUrls = {
    api: "/api/v0/result/",
    tests: "tests",
    testRoot: "/",
    testRootTitle: "Tests",
    results: "/results",
    result: "result",
    breadcrumbTestRootTitle: "",
  };
  if (path=="/result/") {
      testName = location.pathname.substring(8);
      prefix=testName;
      // If the prefix is empty, set it to undefined
      if (prefix === "") {
        prefix = undefined;
      }
      //setUnencodedTestNames([testName]);
      useEffect(() => {
        setLoading(false);
      }, [location]);

  } else if (path=="/tests/" || path=="/"){
//     prefix=path;

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

      // Then fetch summary data for eact test/prefx/subree
//       const summaryPrefix = prefix ? prefix : "";
//       const sumResponse = await fetch("/api/v0/result/"+summaryPrefix+"/summarySiblings", {
//         headers: {
//           "Content-type": "application/json",
//           Authorization: "Bearer " + localStorage.getItem("token"),
//         },
//       });
//
//       if (sumResponse.status != 200) {
//         console.error("Failed to fetch summary of change points: " + sumResponse.status);
//         setSummaries({});
//       }
//
//       const sumJson = await sumResponse.json();
// //       console.debug(sumJson);
// //       setSummaries(sumJson);
//       setLoading(false);
//       populateSummaryData(sumJson);
    };

    useEffect(() => {
      setLoading(true);
      fetchData().finally(()=> setLoading(false));
    }, [location]);



  } else {
    console.warn("Unhandled prefix in URI: " + prefix);
    return (<NoMatch />);
  }
  return (<TableOrResult data={unencodedTestNames}
                         singleTestName={testName}
                         prefix={prefix}
                         summaries={summaries2}
                         setSummaries={setSummaries2}
                         loading={loading}
                         setLoading={setLoading}
                         dashboardType={dashboardTypes.USER}
                         baseUrls={baseUrls}
                         />);

};


export const OrigTestList = ({testNames, shortNames, displayNames, prefix, loading, setLoading, baseUrls, summaries,setSummaries, embed, dashboardType}) => {
  const location = useLocation();
  const [myLoading, setMyLoading] = useState(false);
  const fethSummaryData = async () => {
      const summaryPrefix = prefix ? prefix+"/" : "";
      console.debug(baseUrls);
      const base = baseUrls["api"];
      const sumResponse = await fetch(base + summaryPrefix+"summarySiblings", {
        headers: {
          "Content-type": "application/json",
          Authorization: "Bearer " + localStorage.getItem("token"),
        },
      });

      if (sumResponse.status != 200) {
        console.error("Failed to fetch summary of change points: " + sumResponse.status);
//         setSummaries({});
      }

      const sumJson = await sumResponse.json();
      //setLoading(false);
      populateSummaryData(sumJson, prefix);

  };
  useEffect(()=>{
    fethSummaryData().finally(()=>{return;});
  }, [location]);

  //   const displayNames = shortNames;//.map((name) => decodeURI(name).replace("https://github.com/",""));
  const showGraphs = (ev)=>{
    const body = document.getElementById("showTestListCardBody");
    const body2 = document.getElementById("showGraphsCardBody");
    body.style.display = "none";
    body2.style.display = "block";
    const b = document.getElementById("showListButton");
    const b2 = document.getElementById("showGraphsCardBody");
    b.classList.add("btn-primary");
    b2.classList.remove("btn-primary");
  };
  const ShowGraphsCard = ({
                        testNames,
                    shortNames,
                    prefix,
                    displayNames,
                    baseUrls,
                    breadcrumbName,
                    dashboardType,
                    embed,
                    loading,
                    setLoading,
                    setSummaries,
                    summaries,
                    displayData
  })=>{
    const location = useLocation();
    const [redraw, setRedraw] = useState(1);
    const subtree = testNames.filter((n)=>{return (n.startsWith(prefix)&&prefix!==undefined)});
    const ariaExpanded = localStorage.getItem("showAllGraphs", "false");
    if (subtree.length>0 && subtree.length<30)
        return(
          <>  <div style={{textAlign: "right"}}>
              <button className="btn btn-nothing text-right mt-5 col-xs-6 col-md-5 col-lg-4 col-xl-3" style={{right: 0}} title="Click here to display all graphs on this page" type="button" id="allGraphsButton" data-bs-toggle="collapse"  data-target="#allGraphsPage" href="#allGraphsPage" aria-expanded={ariaExpanded} aria-controls="allGraphsPage"
              onClick={(ev)=>{localStorage.setItem("showAllGraphs", ev.target.attributes["aria-expanded"].value);}}
              >
              ▼ Show graphs here
              </button>
              </div>
              <div>
              <div id="graphs" className="row">
              </div>

              <div className={ariaExpanded=="true"?"":"collapse"} aria-labelledby="allGraphsButton" id="allGraphsPage">

              <div className="card">
                <div className="card-header w-100">All graphs</div>
               <div className="card-body" id="showGraphsCardBody" >
                  <Loading loading={loading} />
                  <DashboardSettings       dashboardType={dashboardType}
                    testName={testNames[0]}
                    loadData={()=>{setRedraw(Math.random())}}
                    displayData={displayData}
                    embed={embed}
                    setGraphSize={setGraphSize}
                  />
                  { localStorage.getItem("showAllGraphs")!="true"? "": (
                  <ManyResultWithTestname
                    testNames={testNames}
                    shortNames={subtree}
                    prefix={prefix}
                    displayNames={displayNames}
                    displayData={displayData}
                    baseUrls={baseUrls}
                    breadcrumbName={prefix}
                    dashboardType={dashboardType}
                    embed={embed}
                    loading={loading}
                    setLoading={setLoading}
                    setSummaries={setSummaries}
                    summaries={summaries}
                    redraw={redraw}
                  />)}
              </div>
              </div>
              </div>
              </div>
            </>
        );
  };


  const defaultGraphSize = localStorage.getItem("graphSize") || "2x1"
  const [graphSize, setGraphSize] = useState(defaultGraphSize);

  return (
    <>
      <div className="container-fluid p-5 text-center benchmark-select col-sm-12 col-lg-11 col-xl-10">
            <div className="container-fluid">
              <div className="card">
                <div className="card-header w-100">Select tests</div>


                <div className="card-body" id="showTestListCardBody">
                  <Loading loading={loading} />
                  <ul className="list-group list-group-flush">
                    <TestList
                      testNames={testNames}
                      shortNames={shortNames}
                      prefix={prefix}
                      displayNames={displayNames}
                      loading={loading}
                      setLoading={setLoading}
                      baseUrls={baseUrls}
                      setSummaries={setSummaries}
                      summaries={summaries}
                    />
                  </ul>
                </div>
              </div>
              <ShowGraphsCard
                    testNames={testNames}
                    shortNames={shortNames}
                    prefix={prefix}
                    displayNames={displayNames}
                    baseUrls={baseUrls}
                    breadcrumbName={prefix}
                    dashboardType={dashboardType}
                    embed={embed}
                    loading={loading}
                    setLoading={setLoading}
                    setSummaries={setSummaries}
                    summaries={summaries}

              />
              <div className="card">
                <div className="card-body create-new-test">
                  <Link to="/docs/getting-started" className="btn btn-success col-xs-6 col-md-5 col-lg-4 col-xl-3">
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

const ManyResultWithTestname = ({
  testNames,
                    shortNames,
                    prefix,
                    displayNames,
                    displayData,
  baseUrls,
  breadcrumbName,
  dashboardType,
  embed,
  loading,
  setLoading,
  setSummaries,
  summaries,
  redraw
}) => {


  // Check for invalid test name in url
  if (!loading && prefix !== undefined && !validTestName(prefix, testNames)) {
      return <NoMatch />;
  }
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
  if(loading) return "";
  shortNames=shortNames.reduce((total,current)=>{
    if(!Array.isArray(total)) total=[total];
    if(total.indexOf(current)==-1)total.push(current);
    return total;
  });
  if(!Array.isArray(shortNames)) shortNames=[shortNames];
  return shortNames.map((name, index) => {
    const displayName = displayNames[index];
    var longName = prefix === undefined ? name : prefix + "/" + name;
    if (testNames.includes(name)) {
      longName = name;
    }
    longName = decodeURIComponent(decodeURI(longName));
    longName = longName.replace("https://github.com/", "");
    return (
    <div className="row mb-5" key={name}>
          <SingleResultWithTestname
                      title={true}
                      testName={longName}
                      baseUrls={baseUrls}
                      breadcrumbName={name}
                      dashboardType={dashboardType}
                      embed={embed}
                      loading={loading}
                      setLoading={setLoading}
                      setSummaries={setSummaries}
                      summaries={summaries}
                      hideSettings={true}
                      redraw={redraw}
                    />

    </div>
    );
  });
};










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
  const setLayout = (e,setGraphSize) =>{
      const newLayout = e.currentTarget.id.substring(10);
      console.debug(newLayout);
      setGraphSize(newLayout);
      localStorage.setItem("graphSize", newLayout);
      resetOtherButtons(e.currentTarget);
      e.preventDefault();
      e.stopPropagation();
  };
  const GraphSizePicker = ({embed, setGraphSize}) => {
    return (<>
            <div className="card col-md-8">
            <div className="card-header text-center mb-4 mt-3">Choose layout</div>
            </div>
            <div className="card col-md-12">
            <div className="row justify-content-center text-center">
            <a  id="btn-graph-overview" href="#" onClick={(e) => setLayout(e,setGraphSize)} className="btn btn-primary col-sm-4 col-lg-2">
            <img src={graph_4x4} alt="4x4" title="Show graphs in a overview layout"  style={{width:100, height:60}} />
            </a>

            <a  id="btn-graph-sparklines" href="#" onClick={(e) => setLayout(e,setGraphSize)} className="btn btn-primary col-sm-4  col-lg-2">
            <img src={graph_nx1} alt="nx1" title="Show graphs in a sparkline layout"  style={{width:100, height:60}} />
            </a>
            <a  id="btn-graph-2x1" href="#" onClick={(e) => setLayout(e,setGraphSize)} className="btn btn-primary col-sm-4  col-lg-2">
            <img src={graph_2x1} alt="2x1" title="Show 2 large graphs"  style={{width:100, height:60}} />
            </a>
            <a  id="btn-graph-1x1" href="#" onClick={(e) => setLayout(e,setGraphSize)} className="btn btn-primary col-sm-4  col-lg-2">
            <img src={graph_1x1} alt="1x1" title="Show 1 graphfor maximum detail" style={{width:100, height:60}} />
            </a>
            {embed == "yes" ? "" :
            <a  href="?embed=yes" className="btn btn-primary col-sm-4  col-lg-2" style={{backgroundColor: "#ffffffff", minWidth:100, minHeight:70}}><span style={{position: "relative", top: "25%", color: "#999999", fontWeight: "bold", border: "2px solid #999999", padding: "10px"}}>Embed</span></a>

            }
            </div>
            </div>
            </>);
  }

  const DashboardSettings = ({
      dashboardType,
      testName,
      loadData,
      displayData,
      embed,
      setGraphSize,
  })=>{

    const orgName = testName.split("/")[0];  // Not used when not an org

    return (<>
            <div className="text-end mt-3 mb-3" id="dashboard_settings">

            <p id="linkToGraphs" style={{textAlign: "right"}}><a title="Link here" href="#graphs" style={{float: "right"}}>¶</a></p>
            <button className="btn" title="settings" type="button" id="dashboardSettingsButton" data-bs-toggle="collapse"  data-target="#dashboardSettingsCollapse" href="#dashboardSettingsCollapse" aria-expanded="false" aria-controls="dashboardSettingsCollapse"
            >
            <p className="inactive-label small">Configure...</p>
            <span className="bi bi-gear-fill"> </span>
            </button>
            <div id="graphs" className="row">
            </div>

            <div className="collapse text-lg-end" aria-labelledby="dashboardSettingsButton" id="dashboardSettingsCollapse">
              <div  className="card card-body">

            <div className="row justify-content-center text-center">
              <GraphSizePicker embed={embed} setGraphSize={setGraphSize}/>
            </div>

            {!isPublicDashboard(dashboardType) && (
                <>
                <div className="row justify-content-center text-center hunter-settings">
                {dashboardType == dashboardTypes.ORG ?
                  <HunterSettingsOrg orgName={orgName} callback={loadData}/> :
                  <HunterSettings callback={loadData}/>
                }
                </div>
                <div className="row justify-content-center text-center">
                {(displayData&&displayData[displayData.length-1])?
                <div className="card col-md-8">
                <div className="card-header justify-content-center text-center mb-3 mt-5">Publish test results</div>
                <TestSettings
                  dashboardType={dashboardType}
                  testName={testName}
                  attributes={displayData[displayData.length-1].attributes}
                />              </div>
                :""}
              </div>
              </>
            )}
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
  title,
  baseUrls,
  breadcrumbName,
  dashboardType,
  embed,
  hideSettings,
  redraw
}) => {
  const location = useLocation();
  const [loading, setLoading] = useState(true);
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
      console.warn(response);
      setNotFound(true);
      return;
    }
    const resultData = await response.json();
    // Emergency hack: 20+ tables with 1500 points each is too much for my browser
    // TODO: Make this configurable
    // Note that change points in the summary table are over the entire history, you just can't see
    // them on the graphs now. Perhaps a slider to select a time range is needed after all.
    setDisplayData(resultData.slice(-300));

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

  const defaultGraphSize = localStorage.getItem("graphSize") || "2x1"
  const [graphSize, setGraphSize] = useState(defaultGraphSize);

  const loadData = () => {
    if(!loading){
    setLoading(true);
    fetchData().finally(() => {
      setLoading(false);
    });
    }
  };
  useEffect(loadData, [location,redraw]);

  if (!loading && notFound) {
    return <NoMatch />;
  }

  const timestamps = displayData.map((result) => {
    return result.timestamp;
  });

  var metricMap = [];
  displayData.map((result) => {
    result.metrics.map((metric) => {
      metricMap.push({ name: metric.name, unit: metric.unit, direction: metric.direction });
    });
  });

  // Only want unique metric names
  var unique = metricMap.reduce((a, b) => {
    const aIndex = a.findIndex((x) => x.name === b.name);

    if (aIndex === -1) {
      return a.concat([b]);
    } else {
      a[aIndex]=b; //We want the last element to define metric unit and direction
      return a;
    }
  }, []);
  applyHash();
  const orgName = testName.split("/")[0];  // Not used when not an org




  return (
    <>
          {embed == "yes" ? "" :
          <Breadcrumb testName={breadcrumbName} baseUrls={baseUrls} />
          }
          <div className="container">
            <div className="row justify-content-center">
              <ChangePointSummaryTable changeData={changePointData} queryStringTextTimestamp={textTimestamp} loading={loading} title={title}/>
            </div>

            {hideSettings?"":
            <DashboardSettings       dashboardType={dashboardType}
              setGraphSize={setGraphSize}
              testName={testName}
              loadData={loadData}
              displayData={displayData}
              embed={embed}
            />
            }

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

const nameIsGitHubRepo = (name) => {
  return name.toLowerCase().startsWith("https://github.com/");
};

// Create a test list entry element. If the name for this entry
// looks like a GitHub repo, fetch the avatar URL and display it
// alongside the name.
//
// TODO(mfleming) Fetching the avatar url is a really quick way
// to exhaust the GitHub API rate limit. We should cache these.
const TestListEntry = ({ name, longName, baseUrls, testNames, summaries,setSummaries ,setLoading, loading }) => {
  const [imageUrl, setImageUrl] = useState(undefined);

  const fetchImage = async (repo) => {
    const response = await fetch(`https://api.github.com/repos/${repo}`, {
      headers: {
        "Content-type": "application/json",
      },
    });
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
      const url = name;
      const repo = url.replace("https://github.com/", "");
      fetchImage(repo).finally(() => {
      });
    }
  }, [location]);

  if (!nameIsGitHubRepo(name)) {
    return (
      <>
        <div className="row justify-content-center">
          <div className="col">
            {name}{" "}
            <SummarizeChangePoints
              longName={longName}
              summaries={summaries} loading={loading}
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
          {name.replace("https://github.com/", "")}{" "}
          <SummarizeChangePoints
            longName={longName}
            summaries={summaries} loading={loading}
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
            {name.replace("https://github.com/", "")}{" "}
            <SummarizeChangePoints
              longName={longName}
              summaries={summaries} loading={loading}
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


const SummarizeChangePoints = ({ longName, summaries,loading }) => {
  const key = decodeURIComponent(longName).replace("https://github.com","");
  // Later we will use data-longname attribute to read more content from a JSON object we fetch from the server
  return (
        <div
          className="summarize-change-points placeholder-summary"
          style={{
            position: "absolute",
            right: "0.5em",
            top: 0,
            textAlign: "right",
          }}
          data-longname={key}
        >
        </div>);
};

/*
const SummarizeChangePoints = ({ longName, summaries,loading }) => {
  // Too many re-renders... oh well, forced me to make the backend call more efficient instead
  // so thanks React I guess
  const [sumChanges, setSumChanges] = useState(0);
  const [firstChanges, setFirstChanges] = useState("");
//   let sumChanges = 0;
//   let firstChanges = "";
//   const setSumChanges = (v) => sumChanges=v;
//   const setFirstChanges = (v) => firstChanges=v;

  console.debug(loading, summaries, longName);
  if (loading || !summaries || !summaries[longName]){
    return false;
  }
    var newestDate = new Date();
    if (
      summaries[longName].total_change_points &&
      parseInt(summaries[longName].total_change_points)
    ) {
      setSumChanges(summaries[longName]["total_change_points"]);
    }
    if (summaries[longName].newest_time && parseInt(summaries[longName].newest_time)) {
      newestDate = new Date(1000 * parseInt(summaries[longName]["newest_time"]));
      setFirstChanges(newestDate.toLocaleString());
    }

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
*/
// Workaround as this is too comlex for react or something
const populateSummaryData = (sData, prefix) => {
  console.debug(sData);
  const summaryElements = document.getElementsByClassName("summarize-change-points");
  console.debug(summaryElements);
  for(let el of summaryElements){
    let key=el.dataset.longname;
    console.debug(key);
    let a, b, c="";
    var newestDate = new Date();
    if (
      sData[key] &&
      sData[key].total_change_points &&
      parseInt(sData[key].total_change_points)
    ) {
      a = parseInt(sData[key]["total_change_points"]);
    }
    if (sData[key] && sData[key].newest_time && parseInt(sData[key].newest_time)) {
      newestDate = new Date(1000 * parseInt(sData[key]["newest_time"]));
      b = newestDate.toLocaleDateString('fi-FI');
    }
    if (sData[key] && sData[key].newest_test_name ) {
      c = sData[key]["newest_test_name"];
    }

    if (a && b){
      el.innerHTML = populateSummaryInner(a,b,c);
    }
  }
};

const populateSummaryInner = (sumChanges,latestDate, latestTestName) => {
   return '<span className="summarize-cp-sum-total">'+(sumChanges > 0 ? sumChanges : "")+
          '</span><span className="summarize-cp-text summarize-cp-text-changes"> &nbsp;changes</span><br /><span className="summarize-cp-text summarize-cp-text-latest" title="' + latestTestName + '">latest on&nbsp;</span><span className="summarize-cp-first-changes" title="' + latestTestName + '">'+latestDate+'</span>';
};
