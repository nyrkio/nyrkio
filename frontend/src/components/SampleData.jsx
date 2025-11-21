import { set } from "date-fns";
import { useEffect, useState } from "react";
import { DrawLineChart } from "./DrawLineChart";
import tigerBeetleLogo from "../static/tb-logo-black.png";
import tursoLogo from "../static/turso-banner.png";
import kiekerLogo from "../static/kieker-logo.svg";
import { OrigTestList } from "./Dashboard.jsx";
import { PublicDashboard } from "./PublicDashboard";
import { TableOrResult } from "./TableOrResult";
import { parseGitHubRepo, dashboardTypes } from "../lib/utils";


const publicCustomers = [
  ["TigerBeetle", "https://tigerbeetle.com", tigerBeetleLogo, "tigerbeetle/tigerbeetle", "main/devhub", "TPS" ],
  ["Turso", "https://turso.tech", tursoLogo, "tursodatabase/turso", "main/turso/main/Execute__SELECT_1_/limbo_execute_select_1", "time"],
  ["Turso", "https://turso.tech", tursoLogo, "tursodatabase/turso", "main/tpc-h/main/Query__14__/limbo_tpc_h_query/14", "time"],
  ["Turso", "https://turso.tech", tursoLogo, "tursodatabase/turso", "main/nightly/turso/main/Execute__SELECT_1_/limbo_execute_select_1", "time"],
  ["Kiel Universität", "https://kieker-monitoring.net/research/projects/moobench/", kiekerLogo, "shinhyungyang/moobench", "main/Kieker-java", "No instrumentation"]
];

export const SampleData = ( { customerName } ) => {
  const [redraw, setRedraw] = useState(1);
  let customerLogo = tursoLogo;
  let orgRepo = "tursodatabase/turso"
  let customerUrl = "https://turso.tech";
  let testName = "main/nightly/turso/main/Execute__SELECT_1_/limbo_execute_select_1";
  let graphName = "time";
  if (customerName === undefined) {
    const randomNum = Math.floor(Math.random() * (publicCustomers.length));
    const c = publicCustomers[randomNum];
    customerName = c[0];
    customerUrl = c[1];
    customerLogo = c[2];
    orgRepo = c[3]
    testName = c[4];
    graphName = c[5]; // May be undefined
  }
  else {
    for(let i=0; i<publicCustomers.length; i++){
      if ( publicCustomers[i][0] == customerName ) {
        const c = publicCustomers[randomNum];
        customerName = c[0];
        customerUrl = c[1];
        customerLogo = c[2];
        orgRepo = c[3]
        testName = c[4];
        graphName = c[5]; // May be undefined
        break;
      }
    }
  }
  return <SampleDataPublic
            customerName={customerName}
            customerUrl={customerUrl}
            customerLogo={customerLogo}
            orgRepo={orgRepo}
            testName={testName}
            graphName={graphName}
            setRedraw={setRedraw}
            redraw={redraw}
            />
}

const CustomerLogo = ( { customerLogo, customerName, customerUrl }) => {
  return (<>
            <a href={customerUrl} target="_blank" rel="noreferrer">
            <img
              src={customerLogo}
              alt={{customerName} + " logo"}
              title={customerName}
              className="tb-logo"
            />
          </a>
        </>);
      };



const SampleDataPublic = ({customerName, customerUrl, customerLogo, orgRepo, testName, graphName, setRedraw, redraw}) => {
  const [testData, setTestData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [changePointData, setChangePointData] = useState([]);
  const [displayData, setDisplayData] = useState([]);
  const [prefix, setPrefix] = useState(undefined);
  const [publicData, setPublicData] = useState([]);


  const fetchPublicTests = async () => {
    const url = encodeURIComponent("https://github.com/" + orgRepo) + "/" + testName;
    setPrefix(url);
    setPublicData([url]);

  };
  const baseUrls = {
    testRootTitle: "GH Repos",
    api: "/api/v0/public/result/",
    apiRoot: "/api/v0/public/",
    testRoot: "/public",
    results: "/public",
    result: "public",
    tests: "public",
    breadcrumbTestRootTitle: "GitHub Repos",
  };
  useEffect(() => {
    setLoading(true);

    fetchPublicTests().finally(() => {
      setLoading(false);
    });
  }, [location]);

  return (
    <div className="row">
    <div className="container-fluid text-center col-sm-10 col-md-8 col-lg-8 col-xl-8 nyrkio-public-sample  p-3 ">
    <p style={{textAlign: "left", width:"100%", float:"left", display:"inline-block"}}>
    <span style={{display:"inline-block"}}>
    <a id="clickme" href="#clickme" onClick={()=>{const next =redraw+1; setRedraw(next);}}>Show next graph&gt;&gt;&gt;</a></span>
    <span style={{align:"right", textAlign:"right", fontSize: "80%", float:"right"}}> <a href="mailto:helloworld@nyrkio.com">Saw a nice graph?<br />
    Tell us to feature it here.</a></span></p>
    <p>Here is the benchmark data from our friends at <strong>{customerName}</strong></p>
        <p><CustomerLogo customerName={customerName} customerUrl={customerUrl} customerLogo={customerLogo} /></p>
      <div className="row justify-content-center text-center pt-5">
        {loading ? (
          <p>Loading...</p>
        ) : (
          <TableOrResult
            prefix={prefix}
            graphName={graphName}
            data={publicData}
            baseUrls={baseUrls}
            dashboardType={dashboardTypes.PUBLIC}
            loading={loading}
            setLoading={setLoading}
            embed="yes"
            redraw={redraw}
          />
        )}
      </div>
      <hr />
      <div className="row">
        <a href="/public">
          More public test results from other Nyrkiö users...
        </a>
      <hr />
      </div>
      </div>
      </div>
  );
};



