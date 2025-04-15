import { useState } from "react";
import posthog from "posthog-js";
import gh_permissions_img from "../static/github_permissions.png";

export const SignUpPage = () => {
  const formState = {
    Visible: "Visible",
    Registered: "Registered",
  };

  const [showForm, setShowForm] = useState(formState.Visible);
  const handleSignUpClick = () => {
    setShowForm(formState.Visible);
  };

  const [email, setEmail] = useState();
  const [password, setPassword] = useState();

  const signUpSubmit = async (e) => {
    e.preventDefault();
    let credentialsData = new URLSearchParams();
    credentialsData.append("email", email);
    credentialsData.append("password", password);

    const creds = {
      email,
      password,
    };

    const data = await fetch("/api/v0/auth/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(creds),
    });
    if (data.status === 400) {
      await data.json().then((body) => {
        alert(body["detail"]);
      });
    } else {
      setShowForm(formState.Registered);
    }

    // trigger account verification email
    const verificationData = await fetch("/api/v0/auth/request-verify-token", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email: email }),
    });
  };

  /*
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
        setLoggedIn(true);
        localStorage.setItem("loggedIn", "true");
        posthog.capture("user_signed_up", { signup_type: "github" });
      })
      .catch((error) => console.log(error));
  };
  */
  const githubInstall = async(e) => {
    e.preventDefault();
    console.log("Github install");
    const url = " https://github.com/apps/nyrkio/installations/new";
    console.log(url);
    window.location.href = url;
  };

  if (showForm === formState.Visible) {
    return (
      <div id="signup" className="container">
        <div className="row">
          <div className="col">
            <h3 className="text-center mt-5">Create new account</h3>
          </div>
        </div>
        <div className="row ">
          <div className="text-justify mt-5 col-lg-6  "  style={{"paddingRight": "1em"}}>
            <hr />
            <p>           <strong className="nyrkio-accent">Recommended:</strong><br /> Install Nyrkiö as a GitHub app <sup>*</sup>:</p>
            <button className="btn btn-success" onClick={githubInstall}>
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
              Install Nyrkiö GitHub app &nbsp;
            </button>
          </div>

          {/*
          <div className="text-center mt-5 col-lg-4  "  style={{"paddingLeft": "1em"}}>
            <hr />
            <p>GitHub OAuth login only:</p>
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
              Login with GitHub &nbsp;
            </button>
          </div>
          */}
          <div className="text-justify  mt-5 mb-5 col-lg-6" style={{"paddingLeft": "2em"}}>
            <hr />
            <p><strong>Nyrkiö unplugged (no GitHub):</strong><br />
            Just use your email address and choose a password:</p>
            <form onSubmit={signUpSubmit}>
              <div className="mb-3">
                <label htmlFor="emailInput" className="form-label">
                  Email address
                </label>
                <input
                  type="email"
                  className="form-control w-50"
                  id="emailInput"
                  onChange={(e) => setEmail(e.target.value)}
                />
                <label htmlFor="passwordInput" className="form-label">
                  Password
                </label>
                <input
                  type="password"
                  className="form-control w-50"
                  id="passwordInput"
                  onChange={(e) => setPassword(e.target.value)}
                />
                <div id="emailHelp" className="form-text">
                  We'll send you an email once your account is ready.
                </div>
              </div>
              <div className="text-justify">
                <button type="submit" className="btn btn-success">
                  Submit
                </button>
              </div>
            </form>
            <div className="row pt-3">
              <div className="form-text text-justify" >
                  Already have an acccount? <a href="/login">Log in here</a>
              </div>
            </div>
          </div>
        </div>
        <div className="row">
          <div className="text-justify col-lg-4">
            <p><sup>*)</sup>GitHub will ask to grant Nyrkiö the following permissions:</p>
            <img src={gh_permissions_img} alt="Github permissions dialog" width="100%"/>
            <p>You can choose to not grant any one of those permissions. Nyrkiö will
            continue to work without the particular feature.</p>
          </div>
        </div>
      </div>
    );
  } else {
    posthog.capture("user_signed_up", { signup_type: "email" });
    return (
      <div className="container">
        <div className="row mt-5 justify-content-center">
          <div className="col-md-6">
            <h3>Thank you for registering!</h3>
            <p>
              We have sent you an email with a link to confirm your account.
              Once you have confirmed your account, you can log in.
            </p>
          </div>
        </div>
      </div>
    );
  }
};
