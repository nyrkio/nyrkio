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
import '../style/components/sample-data.scss'


const publicCustomers = [
  ["TigerBeetle", "https://tigerbeetle.com", tigerBeetleLogo, "tigerbeetle/tigerbeetle", "main/devhub", "TPS" ],
  ["Turso", "https://turso.tech", tursoLogo, "tursodatabase/turso", "main/turso/main/Execute__SELECT_1_/limbo_execute_select_1", "time"],
  ["Turso", "https://turso.tech", tursoLogo, "tursodatabase/turso", "main/tpc-h/main/Query__14__/limbo_tpc_h_query/14", "time"],
  ["Turso", "https://turso.tech", tursoLogo, "tursodatabase/turso", "main/nightly/turso/main/Execute__SELECT_1_/limbo_execute_select_1", "time"],
  ["Kiel University", "https://kieker-monitoring.net/research/projects/moobench/", kiekerLogo, "shinhyungyang/moobench", "main/Kieker-java", "Binary file"]
];

export const SampleData = ( { customerName } ) => {
  let customerLogo = tursoLogo;
  let orgRepo = "tursodatabase/limbo"
  let customerUrl = "https://turso.tech";
  let testName = "main/turso/main/mvcc-ops-throughput/read";
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
            graphName={graphName} />
}

const CustomerLogo = ( { customerLogo, customerName, customerUrl }) => {
  return (
    <>
      <a href={customerUrl} target="_blank" rel="noreferrer" className="d-block">
        <img
          src={customerLogo}
          alt={{customerName} + " logo"}
          title={customerName}
          className="img-fluid"
        />
      </a>
    </>
  );
};



const SampleDataPublic = ({customerName, customerUrl, customerLogo, orgRepo, testName, graphName}) => {
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

  return (<section className="my-section container text-center nyrkio-public-sample">
      <h2 className="text-primary mb-5">See it for yourself</h2>
      <p className="mb-3">You can browse real, live benchmark results from other Nyrkiö users. The red dots are Change Points reported by Nyrkiö</p>
      <p>Here is the benchmark data from our friends at <strong>{customerName}</strong></p>
      <div className="mx-auto my-6" style={{maxWidth:'380px'}}>
        <CustomerLogo customerName={customerName} customerUrl={customerUrl} customerLogo={customerLogo}/>
      </div>


      <div className="row justify-content-center text-center">
        {loading ? (<p>Loading...</p>) : (<TableOrResult
            prefix={prefix}
            graphName={graphName}
            data={publicData}
            baseUrls={baseUrls}
            dashboardType={dashboardTypes.PUBLIC}
            loading={loading}
            setLoading={setLoading}
            embed="yes"
          />)}
        <a className="btn btn-primary w-auto mt-3" href="/public">
          More test results
        </a>
      </div>
    </section>);
};



