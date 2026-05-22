import { useState, useEffect, useCallback } from "react";
import posthog from "posthog-js";
import gh_permissions_img from "../static/github_permissions.png";
import Icon from "./Icon.jsx";
import { PasswordInput } from "./PasswordInput/PasswordInput.jsx"
import { HighlightLoginSection} from "./HighlightLoginSection.jsx";

export const SignUpPage = () => {

  return (
    <SignUpPage2 />
  );

};

export const SignUpPage2 = () => {
    const formState = {
    Visible: "Visible",
    Registered: "Registered",
    Sent: "Sent email",
  };

  const [showForm, setShowForm] = useState(formState.Visible);


  const nop = () =>{e.preventDefault(); return true;};

  const handleSignUpClick = () => {
    setShowForm(formState.Visible);
  };

//   const [email, setEmail] = useState();
//   const [password, setPassword] = useState();
  const [turnstileId, setTurnstileId] = useState();



  const signUpSubmit = async (e) => {
    e.preventDefault();
    const widgetId = await turnstile.render("#turnstile-container", {
      sitekey: "0x4AAAAAAC8z9zGr6wqM9VgI",
      callback: function (token) {
        console.log("Turnstile token:", token);
        signUpSubmit2(widgetId);
      },
      "error-callback": function (errorCode) {
        console.error("Turnstile error:", errorCode);
      },

    });
    setTurnstileId(widgetId);
  };
  const signUpSubmit2 = async (e) => {
    console.log(e);
    /*
    let newUserData = new URLSearchParams();
    newUserData.append("email", email);
    newUserData.append("password", password);*/
//     console.log(newUserData);
    const email = document.getElementById("emailInput");
    const password = document.getElementById("passwordInput");
    const cfTurnstileResponse = turnstile.getResponse(turnstileId);
    const jdata ={
      "email":email.value,
      "password":password.value,
      "cf-turnstile-response":cfTurnstileResponse,
    }
    console.log(jdata);
    const data = await fetch("/api/v0/auth/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(jdata),
    });
    if (data.status > 299) {
      await data.json().then((body) => {
        alert("Creating your Nyrkiö account failed. " + (data.detail || data.status ) );
      });
      return false;
    } else {
      setShowForm(formState.Registered);
      console.log("User created");
      // Next ping backend again, because FastAPI cannot do two things in one http request...

      const jdata2 = {};
      jdata2.email= email.value;
      jdata2["cf-turnstile-response"] = cfTurnstileResponse;

      console.log(jdata2);
      // Notice how we reuse the same Turnstile response token. While unorthodox
      // This is FastAPI silliness already. The token is stored on the other side,
      // it is not possible to check it twice against the captcha provider.
      const verificationData = await fetch(`/api/v0/auth/request-verify-token?cf-turnstile-response=${cfTurnstileResponse}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(jdata2),
      });
      if(verificationData.status <300){
        setShowForm(formState.Sent);
        console.log("email sent");
      }
      else {
        alert("Your user account is created, but we weren't able to automatically verify your email. Could you please email helloworld@nyrkio.com and we'll have you back to benchmarking in a whiff.");
      }

    }
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

  if (showForm === formState.Visible || showForm == formState.Registered) {
    return (
      <div id="signup">
        <HighlightLoginSection title="Create new account">
          <h2 className="h3 text-secondary mb-2">Recommended:</h2>
          <p className="mb-3 mb-md-5">Create account &amp; Install Nyrkiö as a <a href="#github_note" id="github_note_text">GitHub&nbsp;app<sup>*</sup></a>:</p>
          <button className="btn btn-primary d-inline-flex align-items-center justify-content-center gap-2 w-100 w-md-auto" onClick={githubInstall}>
            <Icon name="github-circle"/>
            Install Nyrkiö GitHub app &nbsp;
          </button>

          <hr className="my-4 my-md-5"/>

          <h2 className="h3 text-secondary mb-2">Create account without GitHub integration:</h2>
          <form onSubmit={e => nop()}>
            <div className="mb-3 text-start">
              <label htmlFor="emailInput" className="form-label">
                Email address
              </label>
              <input
                type="email"
                className="form-control"
                placeholder="Enter Email Address"
                id="emailInput"
              />
            </div>
            <div className="text-start">
              <label htmlFor="passwordInput" className="form-label">
                Password
              </label>
              <PasswordInput
                id="passwordInput"
                placeholder="Enter your Password"
              />
            </div>
            <button type="submit" className="btn btn-primary mt-4 w-100 w-md-auto" onClick={signUpSubmit}>Submit</button>

            <div id="turnstile-container" className="mt-4"></div>

            <hr className="my-4 my-md-5"/>

            <p className="mb-1 fw-normal">Already have an account? <a href="/login">Log&nbsp;in&nbsp;here</a></p>
            <p className="mb-0 fw-normal">Have an account but forgot the password? <a href="/forgot-password">Reset&nbsp;password&nbsp;here</a></p>
          </form>
        </HighlightLoginSection>
        <div className="container">
          <div id="github_note" className="text-center mt-5 mt-md-7 w-100 mx-auto" style={{maxWidth: "480px"}}>
            <p className="text-secondary text-start">*) GitHub will ask to grant Nyrkiö the following permissions:</p>
            <div className="p-3 border border-secondary rounded-2 shadow d-inline-block">
              <img src={gh_permissions_img} alt="Github permissions dialog" className="img-fluid"/>
            </div>

            <p className="mt-4 fw-normal">You can choose to not grant any one of those permissions.
              Nyrkiö&nbsp;will continue to work without the particular feature. <a href="#github_note_text">↩</a>
            </p>
          </div>
        </div>
      </div>
    );
  }
  if (showForm == formState.Registered){
    posthog.capture("user_signed_up", { signup_type: "email" });
    return (
      <HighlightLoginSection title="Thank you for registering!">
        <p>Your Nyrkiö account is now created, but before you can login, we want to verify your email address. I'm trying to send you an email now....</p>
        <p className="mb-0">You can also just email us at <a href="mailto:helloworld@nyrkio.com">helloworld@nyrkio.com</a></p>
      </HighlightLoginSection>
    );
  } else if (showForm == formState.Sent){
    posthog.capture("user_verification_requested", { signup_type: "email" });
    return (
      <HighlightLoginSection title="Thank you for registering!">
        <p className="mb-0">
          We have sent you an email with a link to confirm your account.<br className="d-none d-md-block"/>
          Once you have confirmed your account, you can log in.
        </p>
      </HighlightLoginSection>
    );
  }
};
