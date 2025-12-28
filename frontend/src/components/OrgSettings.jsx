import { set } from "date-fns";
import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useLocation } from "react-router";
import { throttle } from "../lib/utils";
import { Modal } from "react-bootstrap";

export const OrgSettings = () => {
  const [validName, setValidName] = useState(false);
  const location = useLocation();
  const path = location.pathname;
  const protocol = window.location.protocol;
  const hostname = window.location.hostname;
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
  useEffect(()=>{
    validateOrgName(orgName,setValidName);
  }
  ,[])
  if (!validName){
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
        <h3 className="text-center" style={{marginBottom: 0}}><span className="bi bi-people-fill"></span> {orgName}</h3>
        <p className="text-center">
           <a href={"/orgs/"+orgName}  style={{color: "#999999"}}>Test results: {protocol}//{hostname}/orgs/{orgName}</a>
           <br />
           <a href={"https://github.com/orgs/"+orgName+"/people"}  style={{color: "#999999"}}>Org membership: https://github.com/orgs/{orgName}</a>
        </p>
        <HunterSettingsOrg orgName={orgName} />
        <NotificationSettings orgName={orgName} />
        <SlackSettings orgName={orgName} />
      </div>
    </>
  );
};

const noop = ()=>{return;};

export const HunterSettingsOrg = ({orgName, callback=noop}) => {


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

    callback();
  };

  const saveHunterSettingsOrg = throttle(saveHunterSettingsOrgReal, 1000);
  const slidersCurrentValue = { min_magnitude_raw: 0, max_pvalue_raw: 0, min_magnitude: 0.05, max_pvalue: 0.001 };

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
/*
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
    const v = document.getElementById("nyrkio-min-magnitude-value");
    if(v) v.innerHTML = Math.round(realValue);
    const slider = document.getElementById("nyrkio-min-magnitude-slider");
    if (slider) slider.value = rawValue;
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
    const quantized = Math.max(parseFloat(Math.round(logScale).toPrecision(1)) / 1000.0,0.0001);
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
    const v = document.getElementById("nyrkio-p-value-value");
    if(v) v.innerHTML = realValue;
    const slider = document.getElementById("nyrkio-p-value-slider");
    if (slider) slider.value = rawValue;
    return rawValue;
  };
*/

  function saveHunterSettings(){
    saveHunterSettingsOrg();
  }
  function getHunterSettings(){
    getHunterSettingsOrg();
  }
  // These are percentages as used in the UI
  // Note that the API uses decimals. So 5 (%) -> 0.05 in API call.
  const quantizedMagnitudeValues = [0.0, 0.0001, 0.001, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.15, 0.2, 0.25, 0.3, 0.333, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.5, 2.0, 2.5, 3.0, 3.333, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0, 30.0, 31.0, 32.0, 33.0, 33.333, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 99, 100, 150, 200, 250, 300, 333, 400, 500, 600, 700, 800, 900, 1000, 5000, 10000, 50000, 100000];
  const minMagnitudeSliderMax = quantizedMagnitudeValues.length-1;
  const quantizedPValues = [0.000001, 0.00001, 0.0001, 0.001, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.15, 0.2, 0.25, 0.3, 0.333, 0.4, 0.5, 1.0];
  const pValueSliderMax = quantizedPValues.length-1;

  // Use logarithmic mode to allow for more granularity around 0.5 - 5 %.
  const minMagnitudeUpdate = (rawValue) => {
    document.getElementById("nyrkio-min-magnitude-value").innerHTML = quantizedMagnitudeValues[rawValue];
    slidersCurrentValue.min_magnitude = quantizedMagnitudeValues[rawValue];
    slidersCurrentValue.min_magnitude_raw = rawValue;
    saveHunterSettings();
  };
  // Use logarithmic mode to allow for more granularity around 0.5 - 5 %.
  // Disabled for now
  const minMagnitudeUpdateLog = (rawValue) => {
    if(rawValue>2250 && rawValue < 2950)
      document.getElementById("nyrkio-min-magnitude-value").innerHTML = 0.5;
    else
      document.getElementById("nyrkio-min-magnitude-value").innerHTML = Math.round(getRealMinMagnitude(rawValue) );

    saveHunterSettings();
  };
  const getRealMinMagnitude = (rawValue, stoprecursion) => {
    return quantizedMagnitudeValues[rawValue];
  };
  const getRealMinMagnitude_Log = (rawValue, stoprecursion) => {
    const scaledDown = rawValue / 1000.0;
    const logScale = Math.pow(scaledDown, 4) / 100;
    const quantized = parseFloat(
      (Math.round(logScale * 2) / 2.0).toPrecision(2),
    );
    // if(!stoprecursion)
    // console.debug("mrawreal " + rawValue + " " + quantized + " " + getRawMinMagnitude(logScale) + " " + getRawMinMagnitude(quantized) + " " + getRealMinMagnitude(getRawMinMagnitude(quantized),true));
    return quantized;
  };
  const getRawMinMagnitude = (realValue) => {
    realValue = Math.max(quantizedMagnitudeValues[0], realValue);
    let i = 0;
    while (realValue > quantizedMagnitudeValues[i]) {
      i++;
    }
    return i;
  };
  const getRawMinMagnitude_Log = (realValue) => {
    const scaledDown = Math.pow(realValue * 100, 1.0 / 4.0);
    const rawValue = scaledDown * 1000.0;
    return rawValue;
  };

  const minMagnitudeSet = (realValue) => {
    let rawValue = getRawMinMagnitude(realValue);
    document.getElementById("nyrkio-min-magnitude-value").innerHTML = quantizedMagnitudeValues[rawValue];
    slidersCurrentValue.min_magnitude = quantizedMagnitudeValues[rawValue];
    slidersCurrentValue.min_magnitude_raw = rawValue;
    document.getElementById("nyrkio-min-magnitude-slider").value = rawValue;
    return rawValue;
  };
  const minMagnitudeSet_Log = (realValue) => {
    let rawValue = getRawMinMagnitude(realValue);
    if (getRealMinMagnitude(slidersCurrentValue.min_magnitude_raw) == realValue){
      rawValue = slidersCurrentValue.min_magnitude_raw;
    }
    if (document.getElementById("nyrkio-min-magnitude-value")){
      if(rawValue>2250 && rawValue < 2950)
        document.getElementById("nyrkio-min-magnitude-value").innerHTML = 0.5;
      else
        document.getElementById("nyrkio-min-magnitude-value").innerHTML = Math.round(realValue );
      document.getElementById("nyrkio-min-magnitude-slider").value = rawValue;
    }
    return rawValue;
  };

  const pvalueUpdate = (rawValue) => {
    const realPValue = getRealPValue(rawValue);
    slidersCurrentValue.max_pvalue = realPValue;
    slidersCurrentValue.max_pvalue_raw = rawValue;
    document.getElementById("nyrkio-p-value-value").innerHTML = realPValue;
    saveHunterSettings();
  };
  const pvalueUpdate_Log = (rawValue) => {
    document.getElementById("nyrkio-p-value-value").innerHTML =
    getRealPValue(rawValue);
    saveHunterSettings();
  };
  const getRealPValue = (rawValue) => {
    return quantizedPValues[rawValue];
  };
  const getRealPValue_Log = (rawValue) => {
    const scaledDown = rawValue / 100.0;
    const logScale = Math.pow(scaledDown, 3) / 1000;
    const quantized = Math.max(parseFloat(Math.round(logScale).toPrecision(1)) / 1000.0,0.0001);
    //console.debug("prawreal " + rawValue + " " + quantized + " " + getRawPValue(logScale) + " " + getRawPValue(quantized));
    return quantized;
  };
  const getRawPValue = (realValue) => {
    realValue = Math.max(quantizedPValues[0], realValue);
    //     alert(realValue);
    let i = 0;
    while (realValue > quantizedPValues[i]) {
      i++;
    }
    return i;
  };
  const getRawPValue_Log = (realValue) => {
    const scaledDown = Math.pow(realValue * 1000, 1.0 / 3.0);
    const rawValue = scaledDown * 100.0 * 10;
    return rawValue;
  };
  const pvalueSet = (realValue) => {
    let rawValue = getRawPValue(realValue);
    document.getElementById("nyrkio-p-value-value").innerHTML = realValue; //quantizedMagnitudeValues[rawValue];
    slidersCurrentValue.max_pvalue = realValue; // quantizedMagnitudeValues[rawValue];
    slidersCurrentValue.max_pvalue_raw = rawValue;
    document.getElementById("nyrkio-p-value-slider").value = rawValue;
    //     alert(JSON.stringify(slidersCurrentValue));
    return rawValue;
  };
  const pvalueSet_Log = (realValue) => {
    let rawValue = getRawPValue(realValue);
    slidersCurrentValue.max_pvalue_raw = rawValue;
    if (document.getElementById("nyrkio-p-value-value")){
      document.getElementById("nyrkio-p-value-value").innerHTML = realValue;
      document.getElementById("nyrkio-p-value-slider").value = rawValue;
    }
    return rawValue;
  };

  const NyrkioCpSliders = () => {
    return (
      <>
      <div id="nyrkio-cp-sliders">
      <div className="row mt-5 ">
      <div className="col-xs-12 col-md-6 col-lg-6">
      <em>Lower P-values (ex: 0.001) will find the most significant regressions, while minimizing false positives.</em>
      </div>
      <div className="col-xs-0 col-md-1 col-lg-1"></div>
      <div className="col-xs-12 col-md-5 col-lg-5">
      <em>Higher P-values (ex: 0.05) will find more change points.</em>
      </div>
      </div>
      <div className="row mt-4 ">
      <div className="col col-md-12">
      <label htmlFor="nyrkio-p-value-slider" className="form-label">
      P-value:{" "}
      </label>
      </div>
      <div className="col col-md-10">
      <input
      type="range"
      id="nyrkio-p-value-slider"
      name="nyrkio-p-value-slider"
      className="nyrkio-p-value-slider nyrkio-slider"
      style={{ width: "100%" }}
      defaultValue={slidersCurrentValue.max_pvalue_raw}
      min={0}
      max={pValueSliderMax}
      step={1}
      precision={1}
      tooltip="off"
      onChange={(ev) => pvalueUpdate(ev.target.value)}
      />
      </div>
      <div className="col col-md-2">
      <span id="nyrkio-p-value-value" className="form-label">
      {slidersCurrentValue.max_pvalue}
      </span>
      </div>
      </div>
      <div className="row mt-5">
      <div className="col-xs-12 col-md-6 col-lg-6">
      <em>You can filter out regressions that are so small that it's not worth fixing them even if they are "real"/statistically significant.</em>
      </div>
      <div className="col-xs-0 col-md-0 col-lg-1"></div>
      <div className="col-xs-12 col-md-6 col-lg-5">
      <em>For example, you might only care about regressions that are 5% or larger.</em>
      </div>
      </div>

      <div className="row mt-5">
      <div className="col col-md-12">
      <label
      htmlFor="nyrkio-min-magnitude-slider"
      className="form-label"
      >
      Change magnitude:{" "}
      </label>
      </div>
      <div className="col col-md-10">
      <input
      type="range"
      id="nyrkio-min-magnitude-slider"
      name="nyrkio-min-magnitude-slider"
      className="nyrkio-min-magnitude-slider nyrkio-slider"
      style={{ width: "100%" }}
      defaultValue={slidersCurrentValue.min_magnitude_raw}
      min={0}
      max={minMagnitudeSliderMax}
      step={1}
      precision={1}
      tooltip="off"
      onChange={(ev) => minMagnitudeUpdate(ev.target.value)}
      />
      </div>
      <div className="col col-md-2">
      <span id="nyrkio-min-magnitude-value" className="form-label">
      {slidersCurrentValue.min_magnitude}
      </span>
      <span className="form-label">%</span>
      </div>
      </div>
      </div>
      </>
    );
  };



  const NyrkioCpSlidersOff = () => {
    return (
      <>
        <div id="nyrkio-cp-sliders">
          <div className="row mt-5 ">
            <p><em>Lower P-values (ex: 0.001) will find the most significant regressions, while minimizing false positives.<br />
            Higher P-values (ex: 0.05) will find more change points.</em></p>
            <div className="col col-md-12">
              <label htmlFor="nyrkio-p-value-slider" className="form-label">
                P-value:{" "}
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
          <div className="row mt-5">
            <p><em>You can filter out regressions that are so small that it's not worth fixing them even if they are "real"/statistically significant.<br />
            For example, you might only care about regressions that are 5% or larger.</em></p>
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
          <div className="card-header ">Change Point Detection</div>
          <div className="card-body">
            <p className="card-text">
              These settings apply for all {orgName} metrics.
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
          <div className="card-header ">Slack</div>
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



const validateOrgName = (checkOrgName, setValidName) => {


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
      if(!found){
        console.error(checkOrgName + " not found in [" + temp + "]");
        return false;
      } else {
        return true;
      }
    }
  };

  return getOrganizations(checkOrgName).then((valid)=>{setValidName(valid);});
};


const NotificationSettings = ({orgName}) => {

  const defaultConfig = {slack: false, github:true, since_days: 14};
  const [notifiersConfig, setNotifiersConfig] = useState(defaultConfig);
  const [githubCheckbox, setGithubCheckbox] = useState(defaultConfig.github);
  const [githubPrCheckbox, setGithubPrCheckbox] = useState(defaultConfig.github);
  const [daysSince, setDaysSince] = useState(defaultConfig.since_days);
  const fetchNotificationConfig = async () => {
    const response = await fetch(`/api/v0/orgs/org/${orgName}`, {
      headers: {
        "Content-type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    });
    if (response.status == 200) {
      console.debug(response);
    } else if (response.status == 401){
      console.debug("User has logged out or wrong password or whatever");
    } else {
      console.error("Failed to GET Nyrkiö notification org settings");
      console.log(response);
      return {defaultConfig};
    }

    const data = await response.json();
    console.debug(data);
    if (
      data &&
      data.notifiers &&
      Object.keys(data).length > 0 &&
      data.hasOwnProperty("notifiers") &&
      Object.keys(data.notifiers).length > 0
    ) {

      return data.notifiers;
    }

    return defaultConfig;
  };

  const saveNotificationConfig = async (c) => {
    const response = await fetch(`/api/v0/orgs/org/${orgName}`, {
      method: "POST",
      headers: {
        "Content-type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
      body: JSON.stringify({notifiers: c})
    });
    if (response.status == 200) {
      console.debug(response);
    } else if (response.status == 401){
      console.debug("User has logged out or wrong password or whatever");
    } else {
      console.error("Failed to save Nyrkiö notification org settings (POST)");
      console.log(response);
    }
  };

  useEffect(() => {
    fetchNotificationConfig().then((c) => {
      setNotifiersConfig(c);
      setGithubCheckbox(c.github?true:false)
      setDaysSince(c.since_days?c.since_days:0)
      setGithubPrCheckbox(c.github_pr?true:false)
      console.log(notifiersConfig);
    });
  }, []);

  const toggleGithub = async (e) => {
    setGithubCheckbox(e.target.checked);

    const c = notifiersConfig;
    c.github = e.target.checked;
    await saveNotificationConfig(c);
    setNotifiersConfig(c);
  };
  const changeDays = async (e) => {
    setDaysSince(e.target.value);

    const c = notifiersConfig;
    c.since_days = e.target.value;
    console.log(c);
    await saveNotificationConfig(c);
    setNotifiersConfig(c);
  };
  const toggleGithubPr = async (e) => {
    setGithubPrCheckbox(e.target.checked);

    const c = notifiersConfig;
    c.github_pr = e.target.checked;
    await saveNotificationConfig(c);
    setNotifiersConfig(c);
  };
  return (
    <div className="row pt-5 justify-content-center">
    <div className="col-md-8">
    <div className="card justify-content-left">
    <div className="card-header">Notification settings</div>
    <div className="card-body" style={{textAlign:"left"}}>
    <form>
    <p>
    <input type="checkbox" id="notifiers_github_issues" name="notifiers_github_issues" checked={githubCheckbox} onChange={(e) => toggleGithub(e)}/>{" "}
    Create a GitHub issue if a change point was found and the commit is at most
    <br />
    <input style={{width: "3em", textAlign: "right"}} type="text" id="notifiers_since_days" name="notifiers_since_days" value={daysSince} onChange={(e)=>changeDays(e)}/>{" "}
    days old. (At most one issue per commit is created.)
    </p>
    <p>
    <input type="checkbox" id="notifiers_github_pr" name="notifiers_github_pr" checked={githubPrCheckbox} onChange={(e) => toggleGithubPr(e)}/>{" "}
    Post a comment on pull requests.
    </p>
    </form>
    </div>
    </div>
    </div>
    </div>
  );
};
