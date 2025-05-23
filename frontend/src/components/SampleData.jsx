import { set } from "date-fns";
import { useEffect, useState } from "react";
import { DrawLineChart } from "./DrawLineChart";
import { ChangePointSummaryTable } from "./ChangePointSummaryTable";
import tigerBeetleLogo from "../static/tb-logo-black.png";
import tursoLogo from "../static/turso-banner.png";
import { OrigTestList } from "./Dashboard.jsx";
import { PublicDashboard } from "./PublicDashboard";
import { TableOrResult } from "./TableOrResult";
import { parseGitHubRepo, dashboardTypes } from "../lib/utils";


export const SampleData = ( { customerName, customerUrl } ) => {
  let customerLogo = tursoLogo;
  let orgRepo = "tursodatabase/limbo"
  let testName = "main/turso/main/mvcc-ops-throughput/read";
  if (customerName === undefined) {
    customerName = "Turso";
    customerUrl = "https://turso.tech";
  }
  if (customerName=="TigerBeetle"){
    return SampleDataTigerBeetle();
  }
  if (customerName=="Turso"){
    customerLogo = tursoLogo;
    orgRepo = "tursodatabase/limbo"
    // testName = "main/turso/main/mvcc-ops-throughput/read";
    testName = "main/turso/main/Execute__SELECT_1_/limbo_execute_select_1";
  }
  return <SampleDataPublic
            customerName={customerName}
            customerUrl={customerUrl}
            customerLogo={customerLogo}
            orgRepo={orgRepo}
            testName={testName} />
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
}

const SampleDataTigerBeetle = () => {
  const [testNames, setTestNames] = useState([]);
  const [testData, setTestData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [changePointData, setChangePointData] = useState([]);
  const [displayData, setDisplayData] = useState([]);
  const fetchDefaultData = async () => {
    const response = await fetch("/api/v0/default/results");
    const results = await response.json();
    setTestNames(results);

    // TODO(mfleming) Assumes one test for now
    const testName = results[0];
    const d = await fetch(`/api/v0/default/result/${testName}`);
    const resultData = await d.json();
    resultData.sort((a, b) => {
      return a.timestamp - b.timestamp;
    });

    console.log(resultData[0]);
    setDisplayData(resultData);

    const changes = await fetch(`/api/v0/default/result/${testName}/changes`);
    const changeData = await changes.json();

    // filter out everything except "load_accepted" metric
    var loadAcceptedChangeData = {};
    Object.entries(changeData).forEach(([key, value]) => {
      var values = [];
      value.forEach((change) => {
        change.changes.forEach((c) => {
          if (c.metric === "load_accepted") {
            var newChange = change;
            newChange.changes = [c];
            values.push(newChange);
          }
        });
      });
      loadAcceptedChangeData[key] = values;
    });

    setChangePointData(loadAcceptedChangeData);
  };

  const displayTigerbeetleData = () => {
    const timestamps = displayData.map((result) => {
      return result.timestamp;
    });

    return testNames.map((testName) => {
      return (
        <div key={testName} className="mt-5">
          <div className="row justify-content-center">
            <ChangePointSummaryTable changeData={changePointData} />
          </div>
          <div className="row">
            <DrawLineChart
              changePointData={changePointData}
              metric={{ unit: "tx/s", name: "load_accepted" }}
              testName={testName}
              timestamps={timestamps}
              displayData={displayData}
            />
          </div>
        </div>
      );
    });
  };
  useEffect(() => {
    setLoading(true);
    fetchDefaultData().finally(() => setLoading(false));
    return () => {
      setTestNames([]);
      setDisplayData([]);
    };
  }, []);

  return (
    <div className="container mt-5 text-center">
      <div className="row"></div>
      <div className="col">
        <h1>See for yourself!</h1>
        <p>&nbsp;</p>
        <p>Here is the benchmark data from our friends at </p>
        <p>
          <a href="https://tigerbeetle.com/" target="_blank" rel="noreferrer">
            <img
              src={tigerBeetleLogo}
              alt="TigerBeetle logo"
              title="TigerBeetle"
              className="tb-logo"
            />
          </a>
        </p>
      </div>
      <div className="row">
        {loading ? <div>Loading...</div> : displayTigerbeetleData()}
      </div>
      <hr />
      <div className="row">
        <a href="/public">
          More public test results from other Nyrkiö users...
        </a>
      </div>
      <hr />
    </div>
  );
};


const SampleDataPublic = ({customerName, customerUrl, customerLogo, orgRepo, testName}) => {
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
    <div className="container mt-5 text-center">
      <div className="row"></div>
      <div className="col">
        <h1>See for yourself!</h1>
        <p>Here is the benchmark data from our friends at </p>
        <p><CustomerLogo customerName={customerName} customerUrl={customerUrl} customerLogo={customerLogo} /></p>
      </div>
      <div className="row justify-content-center text-center pt-5">
        {loading ? (
          <p>Loading...</p>
        ) : (
          <TableOrResult
            prefix={prefix}
            data={publicData}
            baseUrls={baseUrls}
            dashboardType={dashboardTypes.PUBLIC}
            loading={loading}
            setLoading={setLoading}
            embed="yes"
          />
        )}
      </div>
      <hr />
      <div className="row">
        <a href="/public">
          More public test results from other Nyrkiö users...
        </a>
      </div>
      <hr />
    </div>
  );
};



