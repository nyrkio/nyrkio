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
    console.log("Auth submit: " + username + " " + password.substring(0,2));
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

  function uuidv4() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'
    .replace(/[xy]/g, function (c) {
      const r = Math.random() * 16 | 0,
             v = c == 'x' ? r : (r & 0x3 | 0x8);
             return v.toString(16);
    });
  }

  const redirectUri="https://staging.nyrkio.com/login";
  const oneLoginSubmit = async (e) => {
    e.preventDefault();
    console.log("OneLogin submit");
    const data = await fetch("/api/v0/auth/onelogin/authorize")
    .then((response) => response.json())
    .then((url) => {
      console.log(url);
      const u = url["authorization_url"];
      console.log(u);
      setTimeout(()=>{window.location.href = u;}, 20000);
    })
    .catch((error) => console.log(error));
  };
//   const oneLoginSubmit = async (e) => {
//     e.preventDefault();
//     console.log("onelogin submit");
//     const data = await fetch("https://staging.nyrkio.com/api/v0/auth/onelogin/authorize")
//     .then((response) => response.json())
//     .then((url) => url["authorization_url"])
//     .then((url) => {
//       console.log(url);
//       window.location.href = url;
//     })
//     .catch((error) => console.log(error));
//     };
// const OFFoneLoginSubmit = async (e) => {
//     e.preventDefault();
//     console.log("OneLogin submit");
//     const postData =  `nonce=${uuidv4()}&redirect_uri=${redirectUri}&scope=openid&state=onelogin_success&client_id=204875a0-a341-013e-75df-29e1f863f4bd253438&response_type=id_token`
//     const data = await fetch("https://staging.nyrkio.onelogin.com/oidc/2/auth",
//                             {
//                              method:"POST",
//                              body: postData,
//                              headers: {
//                                 "Content-Type": "application/x-www-form-urlencoded",
//                               },
//                             }
//                         )
//     .then((response) => response.json())
//     .then((url) => url["authorization_url"])
//     .then((url) => {
//       console.log(data);
//       window.location.href = url;
//     })
//     .catch((error) => console.log(error));
//   };

  // If we were redirected here by the OneLogin OAuth flow, we need to stash the
  // username and navigate to the home page.
  //const query = new URLSearchParams(window.location.search);
  if (query.get("onelogin_login") === "success") {
    const username = query.get("username");
    setLoggedIn(true);
    localStorage.setItem("loggedIn", "true");
    localStorage.setItem("username", username);
    localStorage.setItem("authMethod", "oauth");
    localStorage.setItem("authServer", "onelogin.com");
    posthog.capture("login", { property: username });

    //     try {
    //       window.location.href = "/";
    //     } catch (error) {
    //       console.log("gh_login was success, but then something went wrong:")
    //       console.log(error);
    //     }
  }
  // If we were redirected here by the OneLogin OAuth flow, we need to stash the
  // username and navigate to the home page.
  // const query = new URLSearchParams(window.location.search);
  /*const c = new URLSearchParams(document.cookie);
  if (query.get("state") === "onelogin_success") {
    const token = c.get("sub_session_onelogin.com");
    console.log(token);
    console.log(query);
    const username = query.get("username");
    setLoggedIn(true);
    localStorage.setItem("loggedIn", "true");
    localStorage.setItem("username", username);
    localStorage.setItem("authMethod", "oauth");
    localStorage.setItem("authServer", "nyrkio.onelogin.com");
    posthog.capture("login", { property: username });
  */
    //     try {
    //       window.location.href = "/";
    //     } catch (error) {
    //       console.log("gh_login was success, but then something went wrong:")
    //       console.log(error);
    //     }
//   }

  return (
    <div className="container">
      <div className="row">
        <div className="col">
          <h2 className="text-left mt-3">Log In With...</h2>
        </div>
      </div>
      <div className="row ">
      <div className="text-justify mt-3 col-lg-6  sso-login"  style={{"paddingRight": "1em"}}>
        <div className="text-left mt-3 mb-3">
          <button className="text-left btn btn-success col-sm-4" onClick={githubSubmit}>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="25"
              height="16"
              fill="currentColor"
              className="bi bi-github"
              viewBox="0 0 16 16"
            >
              <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8" />
            </svg>{" "}
            GitHub
          </button>
        </div>
        <div className="text-left mt-4 mb-4">
          <form action="https://nyrkio.onelogin.com/oidc/2/auth" method="POST">
          <input type="hidden" name="nonce" value={uuidv4()} />
          <input type="hidden" name="redirect_uri" value={redirectUri} />
          <input type="hidden" name="scope" value="openid" />
          <input type="hidden" name="client_id" value="204875a0-a341-013e-75df-29e1f863f4bd253438" />
          <input type="hidden" name="response_type" value="id_token" />
          <input type="hidden" name="state" value="onelogin_success" />
          </form>

          <button className="btn-info btn col-sm-4" onClick={oneLoginSubmit}  style={{"height":"3em", "maxHeight":"3em"}}>
          <svg
          xmlns="http://www.w3.org/2000/svg"
          width="25"
          height="20"
          fill="currentColor"
          className="bi"
          viewBox="-40 -57 100 105"
          >
          <path
          fill="#ffffff"
          d="m -1.1259762,-57.653222 c -27.8865388,0 -50.5505098,22.618369 -50.5505098,50.5052342 0,27.9322898 22.618371,50.5506448 50.5505098,50.5506448 27.9322382,0 50.5508382,-22.618355 50.5508382,-50.5506448 0,-27.8868652 -22.6186,-50.5052342 -50.5508382,-50.5052342 z"
          />
          <path
          fill="#b28b56"
          d="m 6.4135741,10.746842 c 0,0.9538 -0.4998967,1.45342 -1.4534901,1.45342 h -9.0836437 c -0.9536934,0 -1.45349,-0.49962 -1.45349,-1.45342 v -21.891638 h -6.9490583 c -0.953594,0 -1.452991,-0.49961 -1.452991,-1.45337 v -9.083697 c 0,-0.9538 0.499397,-1.45337 1.452991,-1.45337 H 5.186984 c 0.9540934,0 1.1809901,0.49957 1.1809901,1.18085 v 32.701225 z"
          />
          </svg>{" "}
            OneLogin
          </button>
        </div>
      </div>
      <div className="text-center mt-5 col-lg-6 sso-login "  style={{"paddingRight": "1em"}}>
        <div className="row">
        <div className="col-xs-1 col-md-2">
        </div>
        <div className="text-center col-xs-10 col-md-8">
          <form onSubmit={authSubmit}>
            <div className="mb-3 text-center">
              <input
                type="text"
                placeholder="email"
                className="form-control mb-2"
                id="exampleInputEmail1"
                onChange={(e) => setUsername(e.target.value)}
              />
                <input
                  placeholder="passw0rd"
                  type="password"
                  className="form-control mb-2"
                  id="exampleInputPassword1"
                  onChange={(e) => setPassword(e.target.value)}
                />
            </div>
            <div className="text-center mt-2">
              <button type="submit" className="btn btn-info mb-5">
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
