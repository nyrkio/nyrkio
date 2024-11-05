import { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { SingleResultWithTestname } from "./Dashboard";

const UserResults = ({ user, testNames, embed }) => {
  console.log("testname");
  console.log(testNames);

  if (
    testNames === undefined ||
    testNames.length === 0 ||
    Object.keys(testNames).length === 0
  ) {
    return <></>;
  }

  return (
    <div>
      <h2>{user}</h2>
      <ul>
        {testNames.map((testName) => {
          return Object.values(testName).map((testName) => {
            console.log(testName);
            if (testName === undefined || testName.length === 0) {
              return <></>;
            }

            const baseUrls = {
              api: "/api/v0/admin/result/" + user + "/",
              testRoot: "/admin",
              testRootTitle: "Admin",
            };
            return (
              <SingleResultWithTestname
                testName={testName}
                baseUrls={baseUrls}
                breadcrumbName={testName}
                isPublic={false}
                embed={embed}
              />
            );
          });
        })}
      </ul>
    </div>
  );
};
const UserTable = ({ data }) => {
  console.log("data is");
  console.log(data);
  return (
    <div className="row">
      <ul>
        {Object.entries(data).map(([user, testName]) => {
          return (
            <li className="list-group-item">
              <Link to={`/admin/tests/${user}`}>{user}</Link>
            </li>
          );
        })}
      </ul>
    </div>
  );
};

const MainAdminDashboard = ({ results }) => {
  return (
    <>
      <div className="container col-10">
        <h1>Admin Dashboard</h1>
        <div>
          <div className="card">
            <div className="card-header">All user tests</div>
            <div className="card-body">
              <ul className="list-group list-group-flush">
                <UserTable data={results} />
              </ul>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

const AdminUserResults = ({ user, results }) => {
  const testNames = results[user];
  return <UserResults user={user} testNames={testNames} />;
};

export const AdminDashboard = () => {
  const location = useLocation();
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([{}]);
  const fetchData = async () => {
    const results = await fetch("/api/v0/admin/results", {
      headers: {
        "Content-type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    });
    const resultData = await results.json();
    console.log(resultData);
    setResults(resultData);
  };

  useEffect(() => {
    setLoading(true);
    fetchData().finally(() => {
      setLoading(false);
    });
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (location.pathname.startsWith("/admin/tests")) {
    const user = location.pathname.split("/")[3];
    return (
      <>
        <AdminUserResults user={user} results={results} />
      </>
    );
  } else {
    return <MainAdminDashboard results={results} />;
  }
};
