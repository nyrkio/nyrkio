import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import posthog from "posthog-js";
import { SignUpPage } from "./SignUp"

export const ForgotPassword = () => {
  const [errorText, setErrorText] = useState("");
  const [secondPhase, setSecondPhase] = useState(false);
  const [queryParams, setQueryParams] = useSearchParams();




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

  const emailSubmit = async (e) => {
    e.preventDefault();
    const form = e.target;
    const email = form.elements[0].value;

    console.log("email submit: " + email);
    posthog.capture("forgot-password", { property: email });

    const data = await fetch("/api/v0/auth/forgot-password", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({"email": email}),
    })
    .then( (response) => {
      const successText = "We have sent a link to your email that you can use to reset your password. Please check your spam folder. If you didn't receive an email in the next 10 minutes, please email helloworld@nyrkio.com and we will help.";
      if (response.ok) {
        setSecondPhase(true);
        const repe = response.json();

        if (repe.status){
          if (repe.detail) setErrorText(repe.status + " " + repe.detail);
          else setErrorText(repe.status + ": " + successText);
        }
        setErrorText(successText);

      } else {
        console.error(
          "Forgot password request failed: " +
          response.status +
          " " +
          response.statusText,
        );
        setErrorText(
          "Forgot password request failed: " +
          response.status +
          " " +
          response.statusText +
          ")",
        );
      }
    });
  };


  const RequestForm = () => {
    return (
      <div id="request_form" className="mt-3 mb-3 row col-xs-8">
      <div>
      &nbsp;
      </div>
      <form className="row mt-1 sso-login text-center" onSubmit={emailSubmit}>
            <div className="col-md-3">
            &nbsp;
            </div>
            <div className="col-xs-6 col-md-6">
            <input
                type="text"
                placeholder="myemail@example.com"
                className="form-control"
                id="email"
                name="email"
                style={{lineHeight:"0"}}
                />
          <br                   style={{lineHeight:"10px"}}
          />
            </div>
            <br />
            <div className="text-center mb-4 mt-3 xs-12">
            <button type="submit" className="btn-success btn passreset xs-12" style={{minWidth:"12em"}}>
                Send email to reset your password
              </button>
            </div>
          </form>
        </div>

    );
  };
  const SetPassword = ({token}) => {
    const [errorText2, setErrorText2] = useState("");
    const ErrorMessage2 = () => {
      if (errorText2) {
        return (
          <>
          <div className="alert alert-warning mt-3" role="alert">
          {errorText2}
          </div>
          </>
        );
      }
      return "";
    };
    const newPasswordSubmit = async (e) => {
      e.preventDefault();
      const form = e.target;
      const token = form.elements[0].value;
      const password = form.elements[1].value;

      posthog.capture("reset-password", { property: email });

      const data = await fetch("/api/v0/auth/reset-password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({"token": token, "password": password}),
      })
      .then( (response) => {
        const successText = 'Your password was successfully reset. You can now <a href="/login">try to login</a> using your new password';
      if (response.ok) {
        const repe = response.json();

        if (repe.status){
          if (repe.detail) setErrorText2(repe.status + " " + repe.detail);
          else setErrorText2(repe.status + ": " + successText);
        }
        setErrorText2(successText);

      } else {
        console.error(
          "Setting new password request failed: " +
          response.status +
          " " +
          response.statusText,
        );
        setErrorText2(
          "Setting new password request failed: " +
          response.status +
          " " +
          response.statusText,
        );
      }
      });
    };


    return (
      <div id="set_password_form" className="mt-3 mb-3 row col-xs-8">
      <div>
      &nbsp;
      </div>
      <form className="row mt-1 passreset text-center" onSubmit={newPasswordSubmit}>
            <div className="col-md-3">
            &nbsp;
            </div>
            <div className="col-xs-6 col-md-6">
            <p>Token we sent you:</p> <input
                type="text"
                placeholder="[token was sent to your email]"
                defaultValue={queryParams.get("token")}
                className="form-control"
                id="token"
                name="token"
                style={{lineHeight:"0"}}
                />
          <br                   style={{lineHeight:"10px"}}
          />
            <p>New password:</p> <input
                type="password"
                className="form-control"
                id="new_password"
                name="new_password"
                style={{lineHeight:"0"}}
                />
          <br                   style={{lineHeight:"10px"}}
          />
            </div>
            <br />
            <div className="text-center mb-4 mt-3 sso-login xs-12">
            <button type="submit" className="btn-success btn col-xs-12" style={{minWidth:"12em"}}>
                Set new password
              </button>
            </div>
          </form>
          <ErrorMessage2 className="mb-5"/>
          </div>
    );
  };

  return (
    <div>
        <RequestForm />
        <div className="row">
          <ErrorMessage className="mb-5"/>
        </div>
        {secondPhase || queryParams.get("token") ? <SetPassword /> : ""}
      </div>
  );
};


