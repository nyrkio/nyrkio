import { useState } from "react";
import { Link } from "react-router-dom";
import posthog from "posthog-js";
import { SignUpPage } from "./SignUp"
import Icon from './Icon.jsx';
import { PasswordInput } from "./PasswordInput/PasswordInput.jsx";
import { HighlightLoginSection } from "./HighlightLoginSection.jsx";

export const Login = ({ loggedIn, setLoggedIn }) => {
  const [username, setUsername] = useState();
  const [password, setPassword] = useState();
  const [errorText, setErrorText] = useState("");

  const ErrorMessage = () => {
    if (errorText) {
      return (
        <>
          <div className="alert alert-danger mt-3 d-flex flex-nowrap" role="alert">
            <Icon name="triangle-exclamation" size="24" className="flex-shrink-0 me-2"/>
            <div className="text-start">{errorText}</div>
          </div>
        </>
      );
    }
    return "";
  };

  const authSubmit = async (e) => {
    e.preventDefault();
    let credentialsData = new URLSearchParams();
    credentialsData.append("username", username);
    credentialsData.append("password", password);

    try {
      const response = await fetch("/api/v0/auth/cookie/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: credentialsData,
        credentials: "include",
      });

      if (!response.ok) {
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
        return;
      }

      console.log("Logged in. (" + username + ")");
      setErrorText("");
      setLoggedIn(true);

      localStorage.removeItem("token");
      localStorage.setItem("username", username);
      localStorage.setItem("username_real", username);
      localStorage.setItem("authMethod", "password");
      localStorage.setItem("authServer", "nyrkio.com");

      posthog.capture("login", { property: username });
      try {
        window.location.href = "/";
      } catch (error) {
        console.log(error);
      }
    } catch (error) {
      console.log(error);
      setErrorText("Authentication to Nyrkiö.com failed!");
      setLoggedIn(false);
    }
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
    localStorage.removeItem("token");
    localStorage.setItem("username", username);
    localStorage.setItem("authMethod", "oauth");
    localStorage.setItem("authServer", "github.com");
    posthog.capture("login", { property: username });
    window.location.href = "/";
  }

  const redirectUri="https://nyrkio.com/login";
  const ssoSubmit = async (e) => {
    e.preventDefault();
    console.log("SSO submit");
    const oauth_my_domain = document.getElementById("oauth_my_domain").value;
    const oauth_tld = "onelogin.com";
    const startData = await fetch(`/api/v0/auth/start/sso/login?oauth_my_domain=${oauth_my_domain}&oauth_tld=${oauth_tld}`)
      .then((resp) => resp.json())
      .then(async (next) => {
          const data = await fetch(next.next_url)
          .then((response) => response.json())
          .then((url) => {
            console.log(url);
            const u = url["authorization_url"];
            window.location.href = u; // Goes to onelogin.com, from there to the backend, mycallback, and eventually continues below
          })
          .catch((error) => console.log(error));
      })
      .catch((error) => console.log(error));
  };

  if (query.get("sso_login") === "success" && query.get("username") !== undefined && query.get("username") !== "") {
    const username = query.get("username");
    setLoggedIn(true);
    localStorage.removeItem("token");
    localStorage.setItem("username", username);
    localStorage.setItem("authMethod", "oauth");
    localStorage.setItem("authServer", "onelogin.com");
    posthog.capture("login", { property: username });
    window.location.href = "/";
  }

  const urlparams = new URLSearchParams(window.location.search);
  const sso_domain = urlparams.get("sso_domain");
  let sso_domain_default = "";
  if (sso_domain != null) {
    const sso_domain_parts = sso_domain.split(".");
    if (sso_domain_parts.length == 3 && sso_domain_parts[1] == "onelogin" && sso_domain_parts[2]=="com"){
      sso_domain_default = sso_domain_parts[0];
    }
    if (sso_domain_parts.length == 1 && sso_domain.length > 0) {
      sso_domain_default = sso_domain_parts[0];
    }
  }

  const nop = () => {true}

  console.log(sso_domain_default);
  const ssoAutoSubmit = () => {
    if (sso_domain && sso_domain_default) {
      const submitButton = document.getElementById("");
      const e = {};
      e.preventDefault = nop;
      console.log("autoSubmit")
      ssoSubmitButton.click();
    }
  };
  window.addEventListener("load", ssoAutoSubmit);


  return (
    <HighlightLoginSection title="Log in">
      <h2 className="h3 text-secondary mb-3 mb-md-5">Recommended:</h2>
      <button className="btn btn-primary d-inline-flex align-items-center justify-content-center gap-2 w-100 w-md-auto" onClick={githubSubmit}>
        <Icon name="github-circle"/>
        Install Nyrkio Github app
      </button>

      <hr className="my-4 my-md-5"/>

      <h2 className="h3 text-secondary mb-2">Log in</h2>
      <div className="text-start mb-4 mb-md-5">
        <label htmlFor="oauth_my_domain" className="form-label">Domain</label>
        <div className="input-group">
          <input
            type="text"
            defaultValue={sso_domain_default}
            placeholder="Enter your Domain"
            className="form-control"
            id="oauth_my_domain"
            onChange={(e) => setUsername(e.target.value)}
            aria-describedby="oauth_tld"
          />
          <span className="input-group-text oauth_tld bg-primary text-white border-primary fw-semibold" id="oauth_tld">.onelogin.com</span>
        </div>
      </div>

      <button id="ssoSubmitButton" className="btn btn-primary mb-3 w-100 w-md-auto" onLoad={ssoAutoSubmit} onClick={ssoSubmit}>
        OneLogin
      </button>
      <p className="fw-normal">Single Sign on with OneLogin or Okta is available for subscribers.<br/>
        Email <strong>sales@nyrkio.com</strong> and we'll get you connected.</p>

      <hr className="my-4 my-md-5"/>

      <ErrorMessage className="mb-4 mb-md-5"/>
      <form className="sso-login text-start" onSubmit={authSubmit}>
        <div className="mb-3">
          <label htmlFor="exampleInputEmail1" className="form-label">Email Address</label>
          <input
            type="text"
            placeholder="Enter your Email Adress"
            className="form-control"
            id="exampleInputEmail1"
            onChange={(e) => setUsername(e.target.value)}
          />
        </div>
        <div className="mb-3">
          <label htmlFor="exampleInputPassword1" className="form-label">Password</label>
          <PasswordInput
            id="exampleInputPassword1"
            placeholder="Enter your Password"
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <div className="text-center mt-4 mt-md-5">
          <button type="submit" className="btn btn-primary w-100 w-md-auto">Login</button>
        </div>
      </form>

      <hr className="my-4 my-md-5"/>

      <p className="mb-1 fw-normal">Don't have an account? <a href="/signup">Create&nbsp;new&nbsp;account</a></p>
      <p className="mb-0 fw-normal">Have an account but forgot the password? <a href="/forgot-password">Reset&nbsp;password&nbsp;here</a></p>
    </HighlightLoginSection>
  );
};

const logoutTasks = async ({setLoggedIn}) => {
    const response = await fetch("/api/v0/auth/cookie/logout", {
      method: "POST",
      credentials: "include",
    });
    if (response.status !== 200 && response.status !== 204) {
      console.error(
        "Failed to log out: " + response.status + " " + response.statusText,
      );
    }

    console.log("Setting logged in to false");
    setLoggedIn(false);

    localStorage.setItem("username", "");
    localStorage.setItem("username_real", "");
    localStorage.removeItem("token");
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
      <Link to="/" className="btn btn-primary" onClick={handleLogoutClick}>
        Log Out
      </Link>
    </>
  );
};

export const LoginButton = () => {
  return (
    <>
      <Link
        to="/login"
        className="btn btn-primary loginbutton"
      >
        Log In
      </Link>
    </>
  );
};
