import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import posthog from "posthog-js";
import { SignUpPage } from "./SignUp"
import { HighlightLoginSection } from "./HighlightLoginSection.jsx";
import Icon from "./Icon.jsx";
import {PasswordInput} from "./PasswordInput/PasswordInput.jsx";

export const ForgotPassword = () => {
  const [errorText, setErrorText] = useState("");
  const [secondPhase, setSecondPhase] = useState(false);
  const [queryParams, setQueryParams] = useSearchParams();

  const ErrorMessage = () => {
    if (errorText) {
      return (
        <>
          <div className="alert alert-warning d-flex flex-nowrap mt-3" role="alert">
            <Icon name="triangle-exclamation" size="24" className="flex-shrink-0 me-2"/>
            <div
              className="text-start"
              dangerouslySetInnerHTML={{ __html: errorText }}
            />
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
      const successText = "We have sent a link to your email that you can use to reset your password. Please check your spam folder. If you didn't receive an email in the next 10 minutes, please email <a href='mailto:helloworld@nyrkio.com'>helloworld@nyrkio.com</a> and we will help.";
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
      <div id="request_form">
          <form  onSubmit={emailSubmit}>
            <div className="text-start mb-3">
              <label className="form-label" htmlFor="email">Email</label>
              <input
                type="text"
                placeholder="Enter your email"
                className="form-control"
                id="email"
                name="email" />
            </div>
            <div className="text-center mt-4 mt-md-5">
              <button type="submit" className="btn btn-primary passreset w-100 w-md-auto" style={{minWidth:"12em"}}>
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
      <div id="set_password_form">
        <ErrorMessage2 className="mb-3"/>
        <form className="passreset" onSubmit={newPasswordSubmit}>
          <div className="text-start mb-3">
            <label className="form-label" htmlFor="token">Token was sent to your email</label>
            <input
              type="text"
              placeholder="Enter your Token"
              defaultValue={queryParams.get("token")}
              className="form-control"
              id="token"
              name="token"
            />
          </div>
          <div className="text-start">
            <label className="form-label" htmlFor="new_password">New password</label>
            <PasswordInput
              id="new_password"
              name="new_password"
              placeholder="Enter your Password"
            />
          </div>
          <button type="submit" className="btn btn-primary mt-4 mt-md-5 w-100 w-md-auto">
            Set new password
          </button>
        </form>
      </div>
    );
  };

  const isSecondPhase = secondPhase || queryParams.get("token");
  return (
    <HighlightLoginSection title="Reset Password">
      <ErrorMessage className="mb-5"/>

      {!isSecondPhase ? <RequestForm /> : <SetPassword />}

      <hr className="my-4 my-md-5" />

      <p className="mb-0 fw-normal">I remembered it, <a href="/login">Log In</a></p>
    </HighlightLoginSection>
  );
};


