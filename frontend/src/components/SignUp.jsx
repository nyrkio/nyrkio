import { useState } from "react";

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
