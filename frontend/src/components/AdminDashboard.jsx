import { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { SingleResultWithTestname } from "./Dashboard";
import { impersonateUser } from "./ImpersonateControls";

const UserResults = ({ user, testNames, embed }) => {
  console.debug("testname");
  console.debug(testNames);

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
            console.debug(testName);
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
        {Object.entries(data).map(([idx, user]) => {
          return (
            <li className="list-group-item" key={user['_id'] || -1}>
              <Link to={`/`} onClick={(event) => {event.preventDefault(); impersonateUser(user).then(()=>{ window.location.href = '/'})}}>{user['email']}</Link>
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
            <div className="card-header">Impersonate user:</div>
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
    const tempresults = await fetch("/api/v0/admin/all_users", {
      headers: {
        "Content-type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    });
    const resultData = await tempresults.json();
    console.debug(resultData);
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
 return <MainAdminDashboard results={results} />;
};



