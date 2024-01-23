import { useState } from "react";
import { json } from "react-router-dom";

export const SignUpButton = () => {
  const formState = {
    Hidden: "Hidden",
    Visible: "Visible",
    Registered: "Registered",
  };

  const [showForm, setShowForm] = useState(formState.Hidden);
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
      <div className="row mt-5">
        <div className="col-sm-6 offset-sm-3">
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
            <button type="submit" className="btn btn-success">
              Submit
            </button>
          </form>
        </div>
      </div>
    );
  } else if (showForm === formState.Registered) {
    return (
      <div className="row mt-5">
        <div className="col-sm-6 offset-sm-3">
          <h3>Thank you for registering!</h3>
          <p>
            We have sent you an email with a link to confirm your account. Once
            you have confirmed your account, you can log in.
          </p>
        </div>
      </div>
    );
  } else {
    return (
      <div className="row mt-5">
        <div className="d-flex justify-content-center">
          <button className="btn btn-success" onClick={handleSignUpClick}>
            Sign Up
          </button>
        </div>
      </div>
    );
  }
};
