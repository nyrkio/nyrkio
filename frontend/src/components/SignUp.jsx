import { useState } from "react";
import { githubSubmit } from "../lib/github";

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

  if (showForm === formState.Visible) {
    return (
      <div className="container">
        <div className="row">
          <div className="col">
            <h3 className="text-center mt-5">Sign Up</h3>
          </div>
        </div>
        <div className="row">
          <div className="col text-center mt-5">
            <button className="btn btn-success" onClick={githubSubmit}>
              GitHub
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                fill="currentColor"
                className="bi bi-github"
                viewBox="0 0 16 16"
              >
                <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8" />
              </svg>
            </button>
          </div>
        </div>
        <hr className="col-md-5 mx-auto" />
        <div className="row mt-5 justify-content-center">
          <div className="col-md-4">
            <form onSubmit={signUpSubmit}>
              <div className="mb-3">
                <label htmlFor="emailInput" className="form-label">
                  Email address
                </label>
                <input
                  type="email"
                  className="form-control"
                  id="emailInput"
                  onChange={(e) => setEmail(e.target.value)}
                />
                <label htmlFor="passwordInput" className="form-label">
                  Password
                </label>
                <input
                  type="password"
                  className="form-control"
                  id="passwordInput"
                  onChange={(e) => setPassword(e.target.value)}
                />
                <div id="emailHelp" className="form-text">
                  We'll send you an email once your account is ready.
                </div>
              </div>
              <div className="text-center">
                <button type="submit" className="btn btn-success">
                  Submit
                </button>
              </div>
            </form>
            <div className="row pt-5">
              <div className="form-text">
                <p>
                  Already have an acccount? <a href="/login">Log in here</a>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  } else {
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
