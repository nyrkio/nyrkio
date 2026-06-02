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
    <div className="table-responsive rounded shadow">
      <table className="table table-bordered text-center border-light">
        <thead>
        <tr>
          <th>Email</th>
          <th>Active</th>
          <th>Superuser</th>
          <th>Verified</th>
        </tr>
        </thead>

        <tbody>
        {Object.values(data || {}).map((user) => (
          <tr key={user['_id'] || -1}>
            <td className="text-start"><Link to={`/`} onClick={(event) => {event.preventDefault(); impersonateUser(user).then(()=>{ window.location.href = '/'})}}>{user['email']}</Link></td>
            <td>{user.is_active ? "Yes" : "No"}</td>
            <td>{user.is_superuser ? "Yes" : "No"}</td>
            <td>{user.is_verified ? "Yes" : "No"}</td>
          </tr>
        ))}
        </tbody>
      </table>
    </div>
  );
};

const MainAdminDashboard = ({ results }) => {
  return (
    <>
      <div className="container">
        <h1 className="text-center text-primary my-4 my-md-5">Admin Dashboard</h1>
        <UserTable data={results} />
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
      credentials: "include",
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


