import { set } from "date-fns";
import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useLocation } from "react-router";
import { throttle } from "../lib/utils";
import { Modal } from "react-bootstrap";

export const OrgSettings = () => {
  const location = useLocation();
  const path = location.pathname;
  console.debug("OrgSettings: " + path);
  if (! path.startsWith("/org/") ) {
    console.error("Should not be possible, probably a react-router problem? (expected /org/ORG_NAME in URI)")
    return;
  }
  const orgName = path.substring("/org/".length);
  if ( orgName.length == 0 ) {
    console.error("Should not be possible, probably a react-router problem? (expected /org/ORG_NAME in URI)")
    return;
  }
  if (!validateOrgName(orgName)){
      return (
        <>
        <div className="container">
          <strong>Unauthorized / Not found: You are not a member of {orgName}.</strong>
        </div>
        </>
      );
  }

  return (
    <>
      <div className="container text-center">
        <h3 className="text-center">Org: {orgName}</h3>
        <HunterSettings orgName={orgName} />
        <SlackSettings orgName={orgName} />
      </div>
    </>
  );
};


const HunterSettings = ({orgName}) => {


  const saveHunterSettingsOrgReal = async () => {
    const minMagnitude =
      getRealMinMagnitude(
        document.getElementById("nyrkio-min-magnitude-slider").value,
      ) / 100.0;
    const pValue = getRealPValue(
      document.getElementById("nyrkio-p-value-slider").value,
    );
    const configObject = {
      core: { min_magnitude: minMagnitude, max_pvalue: pValue },
    };
    console.debug("POST /api/v0/orgs/org/"+orgName);
    console.debug(configObject);

    const response = await fetch("/api/v0/orgs/org/"+orgName, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
      body: JSON.stringify(configObject),
    });
    if (response.status !== 200) {
      console.error("Failed to POST Nyrkiö org settings for " + orgName);
      console.log(response);
    } else console.debug(response);

  };

  const saveHunterSettingsOrg = throttle(saveHunterSettingsOrgReal, 1000);

  const getHunterSettingsOrg = async () => {
    console.debug("GET /api/v0/orgs/org/"+orgName);
    // TODO(mfleming) It'd be nice to not hard code this.
    // TODO(hingo) yeah actually if we don't get values from the backend it should fail somehow. Now there's a risk of resetting stored values back to defaults. It should only be possible to POST after one successful GET first fetched current values.
    const defaultConfig = { min_magnitude: 0.05, max_pvalue: 0.001 };
    const response = await fetch("/api/v0/orgs/org/"+orgName, {
      headers: {
        "Content-type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    });
    if (response.status !== 200) {
      console.debug("Failed to GET org settings for " + orgName + ". This could be because they don't exist. Using default config values in the meantime.");
      console.log(response);
      return defaultConfig;
    } else console.debug(response);

    const data = await response.json();
    console.debug(data);
    if (
      Object.keys(data).length > 0 &&
      data.hasOwnProperty("core") &&
      Object.keys(data.core).length > 0
    ) {
      //minMagnitudeSet(data.core.min_magnitude);
      //pvalueSet(data.core.max_pvalue);
      return data.core;
    }

    return defaultConfig;
  };

  // Use logarithmic mode to allow for more granularity around 0.5 - 5 %.
  const minMagnitudeUpdate = (rawValue) => {
    document.getElementById("nyrkio-min-magnitude-value").innerHTML =
      getRealMinMagnitude(rawValue);
    saveHunterSettingsOrg();
  };
  const getRealMinMagnitude = (rawValue) => {
    const scaledDown = rawValue / 1000.0;
    const logScale = Math.pow(scaledDown, 4) / 100;
    const quantized = parseFloat(
      (Math.round(logScale * 2) / 2.0).toPrecision(2),
    );
    //console.debug("mrawreal " + rawValue + " " + quantized + " " + getRawMinMagnitude(logScale) + " " + getRawMinMagnitude(quantized));
    return quantized;
  };
  const getRawMinMagnitude = (realValue) => {
    const scaledDown = Math.pow(realValue * 100, 1.0 / 4.0);
    const rawValue = scaledDown * 1000.0;
    return rawValue;
  };
  const minMagnitudeSet = (realValue) => {
    const rawValue = getRawMinMagnitude(realValue);
    document.getElementById("nyrkio-min-magnitude-value").innerHTML =
      Math.round(realValue);
    document.getElementById("nyrkio-min-magnitude-slider").value = rawValue;
    return rawValue;
  };

  const pvalueUpdate = (rawValue) => {
    document.getElementById("nyrkio-p-value-value").innerHTML =
      getRealPValue(rawValue);
    saveHunterSettingsOrg();
  };
  const getRealPValue = (rawValue) => {
    const scaledDown = rawValue / 100.0;
    const logScale = Math.pow(scaledDown, 3) / 1000;
    const quantized = parseFloat(Math.round(logScale).toPrecision(1)) / 1000.0;
    //console.debug("prawreal " + rawValue + " " + quantized + " " + getRawPValue(logScale) + " " + getRawPValue(quantized));
    return quantized;
  };
  const getRawPValue = (realValue) => {
    const scaledDown = Math.pow(realValue * 1000, 1.0 / 3.0);
    const rawValue = scaledDown * 100.0 * 10;
    return rawValue;
  };
  const pvalueSet = (realValue) => {
    const rawValue = getRawPValue(realValue);
    document.getElementById("nyrkio-p-value-value").innerHTML = realValue;
    document.getElementById("nyrkio-p-value-slider").value = rawValue;
    return rawValue;
  };

  const NyrkioCpSliders = () => {
    return (
      <>
        <div id="nyrkio-cp-sliders">
          <div className="row">
            <div className="col col-md-12">
              <label
                htmlFor="nyrkio-min-magnitude-slider"
                className="form-label"
              >
                Change point threshold:{" "}
              </label>
            </div>
            <div className="col col-md-10">
              <input
                type="range"
                id="nyrkio-min-magnitude-slider"
                name="nyrkio-min-magnitude-slider"
                className="nyrkio-min-magnitude-slider nyrkio-slider"
                style={{ width: "100%" }}
                defaultValue={0}
                min={0}
                max={10000}
                step={50}
                precision={50}
                tooltip="off"
                onChange={(ev) => minMagnitudeUpdate(ev.target.value)}
              />
            </div>
            <div className="col col-md-2">
              <span id="nyrkio-min-magnitude-value" className="form-label">
                {0}
              </span>
              <span className="form-label">%</span>
            </div>
          </div>
          <div className="row mt-5 ">
            <div className="col col-md-12">
              <label htmlFor="nyrkio-p-value-slider" className="form-label">
                P-value threshold:{" "}
              </label>
            </div>
            <div className="col col-md-10">
              <input
                type="range"
                id="nyrkio-p-value-slider"
                name="nyrkio-p-value-slider"
                className="nyrkio-p-value-slider nyrkio-slider"
                style={{ width: "100%" }}
                defaultValue={0}
                min={100}
                max={10100}
                step={10}
                precision={10}
                tooltip="off"
                onChange={(ev) => pvalueUpdate(ev.target.value)}
              />
            </div>
            <div className="col col-md-2">
              <span id="nyrkio-p-value-value" className="form-label">
                {0}
              </span>
            </div>
          </div>
        </div>
      </>
    );
  };

  useEffect(() => {
    getHunterSettingsOrg().then((initialConfig) => {
      pvalueSet(initialConfig.max_pvalue);
      minMagnitudeSet(initialConfig.min_magnitude * 100);
    });
  }, [NyrkioCpSliders]);
  return (
    <div className="row pt-5 justify-content-center">
      <div className="col-md-8">
        <div className="card">
          <div className="card-header p-2">Change Point Detection</div>
          <div className="card-body">
            <p className="card-text">
              These settings are global for all your metrics.
            </p>
            <NyrkioCpSliders />
          </div>
        </div>
      </div>
    </div>
  );
};

const SlackSettings = ({orgName}) => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [slackData, setSlackData] = useState([]);

  const doSlackHandshake = async (code) => {
    const response = await fetch("/api/v0/auth/slack/oauth", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
      body: JSON.stringify({ code: code }),
    });
    if (response.status !== 200) {
      console.log("Failed to authenticate with Slack");
      console.log(response);
    }
  };

  const fetchSlackStatus = async () => {
    const defaultConfig = {};
    const response = await fetch("/api/v0/orgs/org/"+orgName, {
      headers: {
        "Content-type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    });
    var data = defaultConfig;
    if (response.status !== 200) {
      console.debug("Failed to GET org settings for " + orgName + ". This could be because they don't exist. Using default config values in the meantime.");
      console.log(response);
    } else {
      console.debug(response);
      data = await response.json();
    }

    if (Object.keys(data).length > 0 && data.slack !== undefined && Object.keys(data.slack).length > 0) {
      setSlackData(data.slack);
    }
  };

  const attemptSlackHandshake = async () => {
    if (searchParams.has("code")) {
      const code = searchParams.get("code");
      if (code) {
        searchParams.delete("code");
        setSearchParams(searchParams);
        await doSlackHandshake(code);
      }
    }
  };

  useEffect(() => {
    attemptSlackHandshake().then(() => {
      fetchSlackStatus();
    });
  }, [searchParams]);

  const slackBtnText =
    Object.keys(slackData).length > 0 ? "Re-connect to Slack" : "Add to Slack";
  return (
    <div className="row pt-5 justify-content-center">
      <div className="col-md-8">
        <div className="card">
          <div className="card-header p-2">Slack</div>
          <div className="card-body">
            {Object.keys(slackData).length > 0 ? (
              <>
                <form>
                  <div className="mb-3 pt-3 col-md-7">
                    <label htmlFor="slackChannel" className="form-label">
                      Sending notifications to:
                    </label>
                    <div className="input-group">
                      <input
                        type="text"
                        className="form-control"
                        id="slackName"
                        value={slackData.team}
                        disabled
                      />
                      <input
                        type="text"
                        className="form-control"
                        id="slackChannel"
                        value={slackData.channel}
                        disabled
                      />
                    </div>
                  </div>
                </form>
              </>
            ) : (
              <>
                <p className="card-text">
                  Nyrkiö can send notifications to Slack when a performance
                  change is detected.
                </p>
              </>
            )}
            <a
              href="https://slack.com/oauth/v2/authorize?scope=incoming-webhook&amp;user_scope=&amp;redirect_uri=https%3A%2F%2Fnyrkio.com%2Fuser%2Fsettings&amp;client_id=6044529706771.6587337889574"
              className="slack-btn"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 122.8 122.8"
                height={20}
                width={20}
              >
                <path
                  d="M25.8 77.6c0 7.1-5.8 12.9-12.9 12.9S0 84.7 0 77.6s5.8-12.9 12.9-12.9h12.9v12.9zm6.5 0c0-7.1 5.8-12.9 12.9-12.9s12.9 5.8 12.9 12.9v32.3c0 7.1-5.8 12.9-12.9 12.9s-12.9-5.8-12.9-12.9V77.6z"
                  fill="#e01e5a"
                ></path>
                <path
                  d="M45.2 25.8c-7.1 0-12.9-5.8-12.9-12.9S38.1 0 45.2 0s12.9 5.8 12.9 12.9v12.9H45.2zm0 6.5c7.1 0 12.9 5.8 12.9 12.9s-5.8 12.9-12.9 12.9H12.9C5.8 58.1 0 52.3 0 45.2s5.8-12.9 12.9-12.9h32.3z"
                  fill="#36c5f0"
                ></path>
                <path
                  d="M97 45.2c0-7.1 5.8-12.9 12.9-12.9s12.9 5.8 12.9 12.9-5.8 12.9-12.9 12.9H97V45.2zm-6.5 0c0 7.1-5.8 12.9-12.9 12.9s-12.9-5.8-12.9-12.9V12.9C64.7 5.8 70.5 0 77.6 0s12.9 5.8 12.9 12.9v32.3z"
                  fill="#2eb67d"
                ></path>
                <path
                  d="M77.6 97c7.1 0 12.9 5.8 12.9 12.9s-5.8 12.9-12.9 12.9-12.9-5.8-12.9-12.9V97h12.9zm0-6.5c-7.1 0-12.9-5.8-12.9-12.9s5.8-12.9 12.9-12.9h32.3c7.1 0 12.9 5.8 12.9 12.9s-5.8 12.9-12.9 12.9H77.6z"
                  fill="#ecb22e"
                ></path>
              </svg>
              {slackBtnText}
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};



const validateOrgName = (checkOrgName) => {


  const username = localStorage.getItem("username");
  const authMethod = localStorage.getItem("authMethod");
  const authServer = localStorage.getItem("authServer");

  const getOrganizations = async () => {
    const url = "/api/v0/orgs/";
    console.debug("GET " + url);
    const response = await fetch(url, {
      headers: {
        "Content-type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    });

    if (response.status !== 200) {
      console.error("Failed to GET User's organizations");
      console.log(response);
      return response;
    } else console.debug(response);

    const data = await response.json();
    console.debug(data);
    if ( Array.isArray(data)  ) {
      return data;
    } else {
      return ["Fetching your organizations failed."];
    }
  };

  return getOrganizations().then((data) => {
    console.debug(data);
    var temp = [];
    data.forEach((d) => {
      temp.push(d.organization.login);
    });
    var found=false;
    temp.forEach((o) => {
      if(o==checkOrgName){
        found=true;
      }
    });
    if(!found) console.error(checkOrgName + " not found in [" + temp + "]");
    return found;

  } );
};
