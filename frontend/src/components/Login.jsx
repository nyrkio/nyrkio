import { useState } from "react";
import { Link } from "react-router-dom";
import posthog from "posthog-js";
import { SignUpPage } from "./SignUp"

export const Login = ({ loggedIn, setLoggedIn }) => {
  const [username, setUsername] = useState();
  const [password, setPassword] = useState();
  const [errorText, setErrorText] = useState("");

  const ErrorMessage = () => {
    if (errorText) {
      return (
        <>
          <div className="alert alert-warning mt-3" role="alert">
            {errorText}
          </div>
        </>
      );
    }
    return "";
  };

  const authSubmit = async (e) => {
    e.preventDefault();
    console.log("Auth submit: " + username + " " + password);
    let credentialsData = new URLSearchParams();
    credentialsData.append("username", username);
    credentialsData.append("password", password);

    const data = await fetch("/api/v0/auth/jwt/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: credentialsData,
    })
      .then((response) => {
        if (response.ok) {
          return response.json();
        } else {
          console.error(
            "Authentication to Nyrkiö.com failed: " +
              response.status +
              " " +
              response.statusText,
          );
          setErrorText(
            "Authentication to Nyrkiö.com failed! (" +
              response.status +
              " " +
              response.statusText +
              ")",
          );
          setLoggedIn(false);
          return false;
        }
      })
      .then((body) => {
        if (!body) {
          console.log("Empty response when logging in. (" +
              response.status +
              " " +
              response.statusText +
              ")");
          setErrorText("Empty response when logging in. ((" +
              response.status +
              " " +
              response.statusText +
              ")");
          setLoggedIn(false);
          return;
        }
        console.log("Logged in. (" + username + ")");
        setErrorText("");
        setLoggedIn(true);

        localStorage.setItem("loggedIn", "true");
        localStorage.setItem("username", username);
        localStorage.setItem("username_real", username);
        localStorage.setItem("token", body["access_token"]);
        localStorage.setItem("authMethod", "password");
        localStorage.setItem("authServer", "nyrkio.com");

        posthog.capture("login", { property: username });
        try {
          window.location.href = "/";
        } catch (error) {
          console.log(error);
        }
      })
      .catch((error) => {
        console.log(error);
      });
  };

  // TODO (mfleming) Move to lib
  const githubSubmit = async (e) => {
    e.preventDefault();
    console.log("Github submit");
    const data = await fetch("/api/v0/auth/github/authorize")
      .then((response) => response.json())
      .then((url) => url["authorization_url"])
      .then((url) => {
        console.log(url);
        window.location.href = url;
      })
      .catch((error) => console.log(error));
  };

  // If we were redirected here by the Github OAuth flow, we need to stash the
  // username and navigate to the home page.
  const query = new URLSearchParams(window.location.search);
  if (query.get("gh_login") === "success") {
    const username = query.get("username");
    setLoggedIn(true);
    localStorage.setItem("loggedIn", "true");
    localStorage.setItem("username", username);
    localStorage.setItem("authMethod", "oauth");
    localStorage.setItem("authServer", "github.com");
    posthog.capture("login", { property: username });

    try {
      window.location.href = "/";
    } catch (error) {
      console.log("gh_login was success, but then something went wrong:")
      console.log(error);
    }
  }

  return (
    <div className="container">
      <div className="row">
        <div className="col">
          <h2 className="text-center mt-5">Log In</h2>
        </div>
      </div>
      <div className="row ">
      <div className="text-justify mt-5 col-lg-6  "  style={{"paddingRight": "1em"}}>
        <div className="text-center mt-5 mb-5">
          <button className="btn btn-success" onClick={githubSubmit}>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              fill="currentColor"
              className="bi bi-github"
              viewBox="0 0 16 16"
            >
              <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8" />
            </svg>{" "}
            Login with GitHub
          </button>
        </div>
      </div>
      <div className="text-center mt-5 col-lg-6  "  style={{"paddingRight": "1em"}}>
        <div className="text-center mt-3 mb-5">
        Or login with your email and password if you created a password account:
        </div>
        <div className="row">
        <div className="col-xs-1 col-md-2">
        </div>
        <div className="text-center col-xs-10 col-md-8">
          <form onSubmit={authSubmit}>
            <div className="mb-3 text-center">
              <label htmlFor="exampleInputEmail1" className="form-label">
                Email address
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
              <button type="submit" className="btn btn-success mb-5">
                Login
              </button>
            </div>
          </form>
        </div>
        </div>
        <ErrorMessage className="mb-5"/>
        </div>
        <div>&nbsp;</div>
        <div>&nbsp;</div>
        <div>&nbsp;</div>
        <div>&nbsp;</div>
        <SignUpPage />
      </div>
    </div>
  );
};

const logoutTasks = async ({setLoggedIn}) => {
    const response = await fetch("/api/v0/auth/jwt/logout", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    });
    if (response.status !== 200 && response.status !== 204) {
      console.error(
        "Failed to log out: " + response.status + " " + response.statusText,
      );
    }

    console.log("Setting logged in to false");
    setLoggedIn(false);

    localStorage.setItem("loggedIn", "false");
    localStorage.setItem("username", "");
    localStorage.setItem("username_real", "");
    document.body.classList.remove( "impersonate-user" );

    posthog.reset();

};

export const LogOut = ({ setLoggedIn }) => {
  const handleLogoutClick = () => {
    logoutTasks({setLoggedIn});
        try {
          window.location.href = "/";
        } catch (error) {
          console.log(error);
        }
  };
  return (
    <>
      <Link to="/" className="btn btn-success" onClick={handleLogoutClick}>
        Log Out
      </Link>
    </>
  );
};

export const LoginButton = ({ loggedIn, setLoggedIn }) => {
  return (
    <>
      <Link
        to="/login"
        className="btn btn-success"
        loggedin={loggedIn}
        setloggedin={setLoggedIn}
      >
        Log In
      </Link>
    </>
  );
};
