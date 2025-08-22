import { set } from "date-fns";
import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { throttle } from "../lib/utils";
import { Modal } from "react-bootstrap";

export const UserSettings = () => {
  return (
    <>
      <div className="container">
        <ApiKey />
        <HunterSettings />
        <SlackSettings />
        <UserInfo />
      </div>
    </>
  );
};

const ApiKey = () => {
  const [apiKey, setApiKey] = useState("");
  const [show, setShow] = useState(false);
  const [buttonText, setButtonText] = useState("Copy");

  const generateApiKey = async () => {
    setShow(true);
    const response = await fetch("/api/v0/auth/token", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    });
    if (response.status !== 200) {
      console.error("Failed to generate API key");
      console.log(response);
      setApiKey(
        "Failed to generate API key: " +
          response.status +
          " " +
          response.statusText,
      );
    } else {
      const data = await response.json();
      setApiKey(data.access_token);
    }
  };

  const handleButtonClick = () => {
    navigator.clipboard.writeText(apiKey);
    setButtonText("Copied!");
  };

  const handleModalClose = () => {
    setShow(false);
    setButtonText("Copy");
  };

  return (
    <>
      <Modal show={show} onHide={handleModalClose} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>API key</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>Your API key is:</p>
          <div className="row">
            <div className="col">
              <input
                type="text"
                value={apiKey}
                readOnly
                className="form-control"
              />
            </div>
            <div className="g-0 col-1">
              <button onClick={handleButtonClick} className="btn btn-success">
                {buttonText}
              </button>
            </div>
          </div>
        </Modal.Body>
      </Modal>

      <div className="row pt-5 justify-content-center">
        <div className="col-md-8">
          <div className="card">
            <div className="card-header p-2">API keys</div>
            <div className="card-body"></div>
            <div className="row">
              <b>
                Please make a copy of your generated API key. It cannot be
                retrieved after closing the dialog.
              </b>
            </div>
            <div className="row p-2">
              <div className="col-6">
                <button className="btn btn-success" onClick={generateApiKey}>
                  Generate API key
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

const noop = ()=>{return;};

// When React redraws this component, try to set default value to what the sliders were,
// rather than making them blink between 0 and real value
const slidersCurrentValue = { min_magnitude_raw: 0, max_pvalue_raw: 0, min_magnitude: 0.05, max_pvalue: 0.001 };

export const HunterSettings = ({callback=noop}) => {
  const saveHunterSettingsReal = async () => {
    slidersCurrentValue.min_magnitude_raw = document.getElementById("nyrkio-min-magnitude-slider").value;
    const minMagnitude =
      getRealMinMagnitude(
        slidersCurrentValue.min_magnitude_raw,
      ) / 100.0;

    slidersCurrentValue.max_pvalue_raw = document.getElementById("nyrkio-p-value-slider").value;
    const pValue = getRealPValue(
      slidersCurrentValue.max_pvalue_raw,
    );
    slidersCurrentValue.max_pvalue = pValue;
    slidersCurrentValue.min_magnitude = minMagnitude;

    const configObject = {
      core: { min_magnitude: minMagnitude, max_pvalue: pValue },
    };
    console.debug("PUT /api/v0/user/config ");
    console.debug(configObject);

    const response = await fetch("/api/v0/user/config", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
      body: JSON.stringify(configObject),
    });
    if (response.status == 200) {
      console.debug(response);
    } else if (response.status == 401){
      console.debug("User has logged out or wrong password or whatever");
    } else {
      console.error("Failed to PUT Nyrkiö core user settings");
      console.log(response);

    }

    caches.delete("nyrkio-changes");
    callback();
  };

  const saveHunterSettings = throttle(saveHunterSettingsReal, 1000);

  const getHunterSettings = async () => {
    console.debug("GET /api/v0/user/config");
    // TODO(mfleming) It'd be nice to not hard code this.
    // TODO(hingo) yeah actually if we don't get values from the backend it should fail somehow. Now there's a risk of resetting stored values back to defaults. It should only be possible to POST after one successful GET first fetched current values.
    //const defaultConfig = { min_magnitude: 0.05, max_pvalue: 0.001 };
    const defaultConfig = slidersCurrentValue;
    const response = await fetch("/api/v0/user/config", {
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
      console.error("Failed to GET Nyrkiö core user settings");
      console.log(response);
      return defaultConfig;
    }

    const data = await response.json();
    console.debug(data);
    if (
      data &&
      data.core &&
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
      if(rawValue>2250 && rawValue < 2950)
        document.getElementById("nyrkio-min-magnitude-value").innerHTML = 0.5;
      else
        document.getElementById("nyrkio-min-magnitude-value").innerHTML = Math.round(getRealMinMagnitude(rawValue) );

    saveHunterSettings();
  };
  const getRealMinMagnitude = (rawValue, stoprecursion) => {
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
    const scaledDown = Math.pow(realValue * 100, 1.0 / 4.0);
    const rawValue = scaledDown * 1000.0;
    return rawValue;
  };
  const minMagnitudeSet = (realValue) => {
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
    document.getElementById("nyrkio-p-value-value").innerHTML =
      getRealPValue(rawValue);
    saveHunterSettings();
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
                defaultValue={slidersCurrentValue.max_pvalue_raw}
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
                {slidersCurrentValue.max_pvalue}
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
                max={10000}
                step={50}
                precision={50}
                tooltip="off"
                onChange={(ev) => minMagnitudeUpdate(ev.target.value)}
              />
            </div>
            <div className="col col-md-2">
              <span id="nyrkio-min-magnitude-value" className="form-label">
                {slidersCurrentValue.min_magnitude*100}
              </span>
              <span className="form-label">%</span>
            </div>
          </div>
        </div>
      </>
    );
  };

  useEffect(() => {
    getHunterSettings().then((initialConfig) => {
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

const SlackSettings = () => {
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
    const response = await fetch("/api/v0/user/config", {
      headers: {
        "Content-type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    });
    const data = await response.json();

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



const UserInfo = () => {


  const username = localStorage.getItem("username");
  const authMethod = localStorage.getItem("authMethod");
  const authServer = localStorage.getItem("authServer");
  const [orgs, setOrgs] = useState([]);

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

  const [ghOrgs, setGhOrgs] = useState([]);
  const [nyrkioOrgs, setNyrkioOrgs] = useState([]);

  useEffect(() => {
    getOrganizations().then((data) => {
      console.log(data);

      var nOrgs = [];
      var gOrgs = [];
      if(data.forEach) {

      var temp = [];
      data.forEach((d) => {
        temp.push(d.organization.login);
      });

      setOrgs(temp);
      temp.forEach((o) => {
        nOrgs.push('<a href="/orgs/'+o+'">nyrkio.com/orgs/'+o+'</a>');
        nOrgs.push(' (<a href="/org/'+o+'">config</a>) <br />');
        gOrgs.push('<a href="https://github.com/orgs/'+o+'">'+o+'</a><br />');
      });


      };

      if(nOrgs.length > 0)  setNyrkioOrgs(nOrgs);
      else setNyrkioOrgs(["😱"]);

      if(gOrgs.length > 0)  setGhOrgs(gOrgs);
      else setGhOrgs(["-"]);

    });
  }, []);

  const DisplayOrgs = () => {
    if(authServer == "github.com" || true){
      return (<>
              <p className="card-text">
                <label>Github Organizations you are a member of:</label> </p>
              <p dangerouslySetInnerHTML={{__html: ghOrgs.join(" ")}}>
              </p>
              <p className="card-text">
                <label>This means you have write permission to the following Nyrkio organizations:</label>
              </p>
                <p dangerouslySetInnerHTML={{ __html: nyrkioOrgs.join(" ") }}></p>
            </>);
    }
  };

  return (
    <div className="row pt-5 justify-content-center">
      <div className="col-md-8">
        <div className="card" id="nyrkio-settings-userinfo">
          <div className="card-header p-2">Information about your user account</div>
          <div className="card-body">
            <p className="card-text">
              <label>Username:</label> {username}
            </p>
            <p className="card-text">
              <label>Authentication method:</label> {authMethod}
            </p>
            <p className="card-text">
              <label>Authentication server:</label> {authServer}
            </p>
            <DisplayOrgs />

            <hr />
            <p className="card-text">If you are a member of a Github org and it isn't shown above, you should request for the Nyrkiö app to be installed specifically to the org you want to post results for. Please click on <a href="https://github.com/apps/nyrkio/installations/new">https://github.com/apps/nyrkio/installations/new</a> and select the org you want to use for nyrkio performance results.</p>
          </div>
        </div>
      </div>
    </div>
  );
};
