import { set } from "date-fns";
import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

export const UserSettings = () => {
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

    if (Object.keys(data).length > 0 && Object.keys(data.slack).length > 0) {
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
    <div className="container">
      <div className="row pt-5 justify-content-center">
        <div className="col-md-8">
          <div className="card">
            <div className="card-header">Slack</div>
            <div className="card-body">
              <h5 className="card-title">Slack Integration</h5>
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
                href="https://slack.com/oauth/v2/authorize?scope=incoming-webhook&amp;user_scope=&amp;redirect_uri=https%3A%2F%2Fnyrk.io%2Fuser%2Fsettings&amp;client_id=6044529706771.6587337889574"
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
    </div>
  );
};
