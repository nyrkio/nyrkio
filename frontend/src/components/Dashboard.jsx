import { createContext, useEffect, useState } from "react";
import { BrowserRouter as Router, Link, useParams } from "react-router-dom";
import { PropTypes } from "prop-types";
import { DrawLineChart } from "./DrawLineChart";
import { ChangePointSummaryTable } from "./ChangePointSummaryTable";


const Breadcrumb = ({ testName }) => {
  const createItems = () => {
    if (testName === undefined) {
      return <></>;
    }

    return testName.split(".").map((name, i) => {
      // Check if we're the last component
      if (i === testName.split(".").length - 1) {
        return (
          <li className="breadcrumb-item active" aria-current="page">
            {name}
          </li>
        );
      }

      var prefix = testName
        .split(".")
        .slice(0, i + 1)
        .join(".");
      return (
        <li className="breadcrumb-item">
          <Link to={`/tests/${prefix}`}>{name}</Link>
        </li>
      );
    });
  };
  return (
    <nav className="navbar navbar-expand-lg">
      <div className="container-fluid breadcrumb-wrapper">
        <nav aria-label="breadcrumb" >
          <ol className="breadcrumb">
            <li className="breadcrumb-item">
              <Link to="/">Tests</Link>
            </li>
            {createItems()}
          </ol>
        </nav>
      </div>
    </nav>
  );
};

export const Dashboard = () => {
  const [loading, setLoading] = useState(false);
  const [testNames, setTestNames] = useState([]);
  var { prefix } = useParams();

  const fetchData = async () => {
    const response = await fetch("/api/v0/results", {
      headers: {
        "Content-type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    });
    const resultData = await response.json();
    resultData.map((element) => {
      const test_name = element.test_name;
      setTestNames((prevState) => [...prevState, test_name]);
    });
  };

  useEffect(() => {
    setLoading(true);
    fetchData().finally(() => {
      setLoading(false);
    });
  }, []);

  if (loading) {
    return <div>Loading</div>;
  }

  var shortNames = [];
  // Initial condition on page load
  if (prefix === undefined) {
    shortNames = testNames
      .map((name) => name.split(".")[0])
      .filter((v, i, a) => a.indexOf(v) === i);
  } else {
    // remove prefix from name
    shortNames = testNames
      .filter((name) => {
        // Prefix must be an exact match
        return (
          name.startsWith(prefix) &&
          name.length > prefix.length &&
          name.substring(prefix.length, prefix.length + 1) === "."
        );
      })
      .map((name) => {
        var shortName = name.replace(prefix + ".", "");
        return shortName.split(".")[0];
      })
      .filter((v, i, a) => a.indexOf(v) === i);
  }

  const createTestList = () => {
    return shortNames.map((name) => {
      var longName = prefix + "." + name;
      if (testNames.includes(longName) || testNames.includes(name)) {
        if (!testNames.includes(longName)) longName = name;
        return (
          <li className="list-group-item">
            <Link to={`/result/${longName}`} state={{ testName: longName }}>
              {name}
            </Link>
          </li>
        );
      } else {
        var p = name;
        if (prefix !== undefined) p = prefix + "." + name;
        return (
          <li className="list-group-item">
            <Link to={`/tests/${p}`} state={{ testName: name }}>
              {name}
            </Link>
          </li>
        );
      }
    });
  };

  return (
    <>
      <Breadcrumb testName={prefix} />
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
                    {createTestList()}
                  </ul>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </>
  );
};

export const SingleResultWithTestname = ({ testName }) => {
  const [loading, setLoading] = useState(false);
  const [displayData, setDisplayData] = useState([]);
  const [changePointData, setChangePointData] = useState([]);
  const fetchData = async () => {
    const results = await fetch("/api/v0/result/" + testName, {
      headers: {
        "Content-type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    });
    const resultData = await results.json();
    resultData.sort((a, b) => {
      return a.timestamp - b.timestamp;
    });
    setDisplayData(resultData);

    const changes = await fetch("/api/v0/result/" + testName + "/changes", {
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

  console.log("Display data");
  console.log(displayData);

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
          <Breadcrumb testName={testName} />
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
  const { testName } = useParams();
  return <SingleResultWithTestname testName={testName} />;
};
