import { useEffect, useState } from "react";
import { dashboardTypes } from "../lib/utils";

// Configure the test settings for a given test.  attributes is the attributes
// field for the most recent test result, and is used when configuring the
// settings for the first time.
export const TestSettings = ({ dashboardType, testName, attributes }) => {
  const [publicTest, setPublicTest] = useState(false);
  const [testConfig, setTestConfig] = useState([]);
  const [loading, setLoading] = useState(true);

  console.debug("dashboardType: " + dashboardType);
  const fetchUrl =
    dashboardType === dashboardTypes.ORG
      ? "/api/v0/orgs/config/"
      : "/api/v0/config/";

  console.debug("testName: " + testName);
  const fetchData = async () => {
    console.debug("Fetching from " + fetchUrl + testName);
    const response = await fetch(fetchUrl + testName, {
      headers: {
        "Content-type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    });

    if (response.status !== 200) {
      console.error("Failed to fetch config for " + testName);
      return;
    }
    const data = await response.json();
    console.debug("Fetched config: " + JSON.stringify(data));
    setTestConfig(data);

    if (data.length > 0 && data[0].public) {
      setPublicTest(true);
    }
  };

  useEffect(() => {
    setLoading(true);
    fetchData().finally(() => {
      setLoading(false);
    });
  }, []);

  if (loading || attributes === undefined) return <> </>;

  const handleToggle = async (value) => {
    var newConfig;
    if (testConfig.length > 0) {
      newConfig = structuredClone(testConfig);
    } else {
      // If there's no existing config, use the attributes from the most recent
      // test result.
      newConfig = [
        {
          attributes: {
            git_repo: attributes.git_repo,
            branch: attributes.branch,
          },
        },
      ];
    }

    newConfig[0].public = value;

    console.debug("Sending new config: " + JSON.stringify(newConfig));
    console.debug("Sending to url: " + fetchUrl + testName);
    const response = await fetch(fetchUrl + testName, {
      method: "POST",
      headers: {
        "Content-type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
      body: JSON.stringify(newConfig),
    });

    if (response.status === 200) {
      setTestConfig(newConfig);
      setPublicTest(value);
    }
  };

  return (
    <>
      <div className="container mb-5">
        <div className="row justify-content-center">
          <div className="col-md-6 justify-content-center">
            <div className="form-check form-switch justify-content-center text-center">
              <input
                className="form-check-input text-center justify-content-center align-items-center"
                onChange={() => handleToggle(!publicTest)}
                type="checkbox"
                role="switch"
                id="flexSwitchCheckUnChecked"
                defaultChecked={publicTest}
              ></input>
              <label
                className="form-check-label"
                htmlFor="flexSwitchCheckUnChecked"
              >
                {publicTest ? (
                  <b>These test results are public</b>
                ) : (
                  <i>These test results are private</i>
                )}
              </label>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};
