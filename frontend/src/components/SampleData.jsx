import { set } from "date-fns";
import { useEffect, useState } from "react";
import { DrawLineChart } from "./DrawLineChart";
import { ChangePointSummaryTable } from "./ChangePointSummaryTable";
import tigerBeetleLogo from "../static/tb-logo-black.png";

export const SampleData = () => {
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
        <p>
          Here is the benchmark data from our friends at{" "}
        </p>
        <p>
          <a href="https://tigerbeetle.com/" target="_blank" rel="noreferrer">
          <img src={tigerBeetleLogo} alt="TigerBeetle logo" title="TigerBeetle" className="tb-logo" />
          </a>
        </p>
      </div>
      <div className="row">
        {loading ? <div>Loading...</div> : displayTigerbeetleData()}
      </div>
      <hr />
      <div className="row">
        <a href="/public">More public test results from other Nyrkiö users...</a>
      </div>
      <hr />
    </div>
  );
};
