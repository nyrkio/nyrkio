import { createContext, useEffect, useState } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link,
  useNavigate,
} from "react-router-dom";
import { Line } from "react-chartjs-2";
// DO NOT REMOVE
// necessary to avoid "category is not a registered scale" error.
import { Chart as ChartJS } from "chart.js/auto";
import { Chart } from "react-chartjs-2";
import { format } from "date-fns";
import { AgGridReact } from "ag-grid-react"; // React Grid Logic
import "ag-grid-community/styles/ag-grid.css"; // Core CSS
import "ag-grid-community/styles/ag-theme-quartz.css"; // Theme
import "./App.css";

const LoggedInContext = createContext(false);

function NoMatch() {
  return (
    <div style={{ padding: 20 }}>
      <h2>404: Page Not Found</h2>
      <p>Lorem ipsum dolor sit amet, consectetur adip.</p>
    </div>
  );
}

async function loginUser(credentials) {
  return fetch("http://localhost:8000/auth/jwt/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: JSON.stringify(credentials),
  }).then((data) => data.json());
}

const Login = ({ loggedIn, setLoggedIn }) => {
  const [username, setUsername] = useState();
  const [password, setPassword] = useState();

  const githubSubmit = async (e) => {
    // e.preventDefault();
    // console.log("Github submit");
    // const data = await fetch("http://localhost/api/v0/auth/github/authorize")
    //   .then((response) => response.json())
    //   .then((url) => url["authorization_url"])
    //   .then((url) => {
    //     console.log(url);
    //     window.location.href = url;
    //     setLoggedIn(true);
    //     localStorage.setItem("loggedIn", "true");
    //   })
    //   .catch((error) => console.log(error));
  };

  const navigate = useNavigate();
  const authSubmit = async (e) => {
    e.preventDefault();
    console.log("Auth submit: " + username + " " + password);
    let credentialsData = new URLSearchParams();
    credentialsData.append("username", username);
    credentialsData.append("password", password);

    const data = await fetch("http://localhost/api/v0/auth/jwt/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: credentialsData,
    })
      .then((response) => response.json())
      .then((body) => {
        setLoggedIn(true);
        localStorage.setItem("loggedIn", "true");
        localStorage.setItem("token", body["access_token"]);
        try {
          navigate("/");
        } catch (error) {
          console.log(error);
        }
      })
      .catch((error) => console.log(error));
  };

  return (
    <div className="row mt-5">
      <div className="col-sm-3 offset-sm-4">
        <form onSubmit={authSubmit}>
          <div className="mb-3">
            <label htmlFor="exampleInputEmail1" className="form-label">
              Username
            </label>
            <input
              type="text"
              className="form-control"
              id="exampleInputEmail1"
              onChange={(e) => setUsername(e.target.value)}
            />
            <div className="mb-3">
              <label htmlFor="exampleInputPassword1" className="form-label">
                Password
              </label>
              <input
                type="password"
                className="form-control"
                id="exampleInputPassword1"
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>
          <div className="text-center mt-2">
            <button type="submit" className="btn btn-success">
              Submit
            </button>
          </div>
        </form>
        {/* <div className="text-center mt-5">
          <button className="btn btn-success" onClick={githubSubmit}>
            Log in with GitHub
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              fill="currentColor"
              className="bi bi-github"
              viewBox="0 0 16 16"
            >
              <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8" />
            </svg>
          </button>
        </div> */}
      </div>
    </div>
  );
};

const LogOut = ({ setLoggedIn }) => {
  const handleLogoutClick = () => {
    console.log("Setting logged in to false");
    setLoggedIn(false);
    localStorage.setItem("loggedIn", "false");
  };
  return (
    <>
      <button className="btn btn-success" onClick={handleLogoutClick}>
        Log Out
      </button>
    </>
  );
};
const LoginButton = ({ loggedIn, setLoggedIn }) => {
  return (
    <>
      <Link
        to="/login"
        className="btn btn-success"
        loggedIn={loggedIn}
        setLoggedIn={setLoggedIn}
      >
        Log In
      </Link>
      {/* <a href="/foobar" className="btn btn-success" type="submit">
          Sign Up
        </a> */}
    </>
  );
};

const NavigationItems = () => {
  return (
    <>
      <button
        className="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarSupportedContent"
        aria-controls="navbarSupportedContent"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span className="navbar-toggler-icon"></span>
      </button>
      <div className="collapse navbar-collapse" id="navbarSupportedContent">
        <ul className="navbar-nav me-auto mb-2 mb-lg-0">
          <li className="nav-item">
            <a className="nav-link" href="#">
              Company
            </a>
          </li>
          <li className="nav-item">
            <a className="nav-link" href="#">
              Product
            </a>
          </li>
          <li className="nav-item">
            <a className="nav-link" href="#">
              Pricing
            </a>
          </li>
          <li className="nav-item">
            <a className="nav-link" href="#">
              Services
            </a>
          </li>
          <li className="nav-item">
            <a className="nav-link" href="#">
              Research
            </a>
          </li>
        </ul>
      </div>
    </>
  );
};

const NavHeader = ({ loggedIn, setLoggedIn }) => {
  return (
    <nav className="navbar navbar-expand-lg">
      <div className="container-fluid">
        <NavigationItems />
        {loggedIn ? <LogOut setLoggedIn={setLoggedIn} /> : <LoginButton />}
      </div>
    </nav>
  );
};

const Banner = () => {
  return (
    <div className="container-fluid border p-5 text-center">
      <h1>Detect every performance change.</h1>
      <h5>
        The performance measurement tool that harnesses the power of change
        point detection
      </h5>
    </div>
  );
};

const FeatureHighlight = () => {
  return (
    <div className="row">
      <div className="col-sm-4">
        <h3>Shift left</h3>
        <p>
          Performance regressions are often only discovered during later stages
          of development such as release candidate testing.
        </p>
        <p>
          Pull your performance testing earlier with Nyrkiö and flag regressions
          as soon as they're committed.
        </p>
      </div>
      <div className="col-sm-4">
        <h3>Automate analysis</h3>
        <p>
          Avoid the tedious work of checking performance dashboards by hand.
        </p>
      </div>
      <div className="col-sm-4">
        <h3>State of the art</h3>
        <p>
          Change point detection is state of the art technology for detecting
          changes in software performance. Used by leading technology companies
          such all around the world including MongoDB and Netflix.
        </p>
      </div>
    </div>
  );
};

const SignUpButton = () => {
  const [showForm, setShowForm] = useState(false);
  const handleSignUpClick = () => {
    setShowForm(true);
    console.log("Sign up clicked");
  };
  if (showForm) {
    return (
      <div className="row mt-5">
        <div className="col-sm-6 offset-sm-3">
          <form>
            <div className="mb-3">
              <label htmlFor="exampleInputEmail1" className="form-label">
                Email address
              </label>
              <input
                type="email"
                className="form-control"
                id="exampleInputEmail1"
              />
              <div id="emailHelp" className="form-text">
                We'll never share your email with anyone else.
              </div>
            </div>
            <button type="submit" className="btn btn-success">
              Submit
            </button>
          </form>
        </div>
      </div>
    );
  } else {
    return (
      <div className="row mt-5">
        <div className="d-flex justify-content-center">
          <button className="btn btn-success" onClick={handleSignUpClick}>
            Sign Up
          </button>
        </div>
      </div>
    );
  }
};

const Root = ({ loggedIn }) => {
  return (
    <>
      <div className="container mt-5 text-center">
        {loggedIn ? (
          <Dashboard />
        ) : (
          <>
            <Banner />
            <FeatureHighlight />
            <SignUpButton />
          </>
        )}
      </div>
    </>
  );
};

const parseTimestamp = (t) => {
  const utcSeconds = t;
  var d = new Date(0);
  d.setUTCSeconds(utcSeconds);
  return format(d, "yyyy-MM-dd HH:mm");
};

const ChangePointSummaryTable = ({ changeData }) => {
  var rowData = [];

  Object.entries(changeData).forEach(([testName, value]) => {
    value.forEach((changePoint) => {
      console.log(changePoint);
      const changes = changePoint["changes"];
      console.log(changes);
      changes.map((change) => {
        rowData.push({
          date: parseTimestamp(changePoint["time"]),
          commit: changePoint["commit"],
          metric: change["metric"],
          change: change["forward_change_percent"] + "%",
        });
      });
    });
  });

  const colDefs = [
    { field: "date" },
    { field: "commit" },
    { field: "metric" },
    { field: "change" },
  ];
  return (
    <>
      <div className="ag-theme-quartz" style={{ height: 500, width: 900 }}>
        <AgGridReact rowData={rowData} columnDefs={colDefs} pagination={true} />
      </div>
    </>
  );
};

const Dashboard = () => {
  const [loading, setLoading] = useState(false);
  const [displayData, setDisplayData] = useState([]);
  const [changePointData, setChangePointData] = useState([]);
  const [testName, setTestName] = useState("");
  const fetchData = async () => {
    const response = await fetch("http://localhost/api/v0/results", {
      headers: {
        "Content-type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    });
    const doMap = async (element) => {
      const test_name = element.test_name;
      setTestName(test_name);
      const results = await fetch(
        "http://localhost/api/v0/result/" + test_name,
        {
          headers: {
            "Content-type": "application/json",
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
        }
      );
      const resultData = await results.json();
      resultData.sort((a, b) => {
        return a.timestamp - b.timestamp;
      });
      setDisplayData(resultData);

      const changes = await fetch(
        "http://localhost/api/v0/result/" + test_name + "/changes",
        {
          headers: {
            "Content-type": "application/json",
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
        }
      );
      const changeData = await changes.json();
      setChangePointData(changeData);
    };
    const data = await response.json();
    const d = data.map(doMap);
  };

  const parseData = (data, metricName) => {
    console.log(data);
    const value_map = data.map(
      (result) =>
        result.metrics
          .filter((metric) => metric.name === metricName)
          .map((metric) => metric.value)[0]
    );
    console.log(value_map);
    return value_map;
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

  // {'testName':
  //    [{
  //      'time': 123,
  //      'changes': [{'forward_change_percent': 900, 'metric': 'metric1'}]
  //    }]
  // }
  var changePointIndexes = [];
  const changePointTimes = [];
  Object.entries(changePointData).forEach(([testName, value]) => {
    value.forEach((changePoint) => {
      changePointTimes.push(changePoint["time"]);
    });
  });

  timestamps.map((timestamp, index) => {
    if (changePointTimes.includes(timestamp)) {
      changePointIndexes.push(index);
    }
  });

  const drawLineChart = (metric) => {
    const metricName = metric["name"];
    const metricUnit = metric["unit"];
    return (
      <>
        <h6 className="text-center">
          {testName}: {metricName}
        </h6>
        <Line
          datasetIdKey="foo"
          data={{
            labels: timestamps.map(parseTimestamp),
            datasets: [
              {
                id: 1,
                label: metricName,
                data: parseData(displayData, metricName),
                pointRadius: (context) => {
                  const c = changePointIndexes;
                  return c.includes(context.dataIndex) ? 8 : 0;
                },
              },
            ],
          }}
          options={{
            scales: {
              x: {
                grid: {
                  display: false,
                },
              },
            },
            plugins: {
              legend: {
                display: false,
              },
              interaction: {
                intersect: false,
                mode: "index",
              },
              tooltip: {
                displayColors: false,
                callbacks: {
                  label: (context) => {
                    var labelArray = ["value: " + context.raw + metricUnit];

                    // Search in changePointData for this timestamp
                    const timestamp = timestamps[context.dataIndex];
                    Object.entries(changePointData).forEach(
                      ([testName, value]) => {
                        value.forEach((changePoint) => {
                          if (changePoint["time"] === timestamp) {
                            labelArray.push("");

                            // Add all change point attributes to the label
                            changePoint["changes"].forEach((change) => {
                              Object.entries(change).map(([key, value]) => {
                                if (key === "metric") {
                                  return;
                                }

                                var label = key + ": " + value;
                                if (key.includes("percent")) {
                                  label = label + "%";
                                }

                                labelArray.push(label);
                              });
                            });
                          }
                        });
                      }
                    );

                    return labelArray;
                  },
                },
                intersect: false,
              },
            },
          }}
        />
      </>
    );
  };

  return (
    <>
      <h1>Dashboard</h1>
      {loading ? (
        <div>Loading</div>
      ) : (
        <>
          <div className="container">
            <div className="row justify-content-center">
              <ChangePointSummaryTable changeData={changePointData} />
            </div>
            <div className="row">{unique.map(drawLineChart)}</div>
          </div>
        </>
      )}
    </>
  );
};

function App() {
  const [count, setCount] = useState(0);
  const [token, setToken] = useState();
  console.log("Resetting");
  const [loggedIn, setLoggedIn] = useState(() => {
    const saved = localStorage.getItem("loggedIn");
    const initialValue = JSON.parse(saved);
    console.log("Reading " + saved);
    return initialValue || false;
  });

  return (
    <>
      <Router>
        <NavHeader loggedIn={loggedIn} setLoggedIn={setLoggedIn} />
        <Routes>
          <Route path="/" element={<Root loggedIn={loggedIn} />} />
          <Route
            path="/login"
            element={<Login loggedIn={loggedIn} setLoggedIn={setLoggedIn} />}
          />
          <Route path="*" element={<NoMatch />} />
        </Routes>
      </Router>
    </>
  );
}

export default App;
