import { useState } from "react";
import { Link } from "react-router-dom";
import { SampleData } from "./SampleData";
import tigerbeetle from "../static/tigerbeetle-change-points.png";
import github from "../static/github.png";
import cicd from "../static/cicd.png";
import commit from "../static/commit.png";

const Banner = () => {
  return (
    <div className="container-fluid p-5 text-center">
      <h1>For Faster Software.</h1>
      <h5>
        Nyrkiö is the performance analysis tool that harnesses the power of
        change point detection
      </h5>
    </div>
  );
};

const FeatureHighlight = () => {
  return (
    <div className="row">
      <div className="col-sm-4">
        <h3>Shift left</h3>
        <p>
          Performance regressions are often only discovered during later stages
          of development such as release candidate testing.
        </p>
        <p>
          Pull your performance testing earlier with Nyrkiö and flag regressions
          as soon as they're committed.
        </p>
      </div>
      <div className="col-sm-4">
        <h3>Automate analysis</h3>
        <p>
          Avoid the tedious work of checking performance dashboards by hand.
          Receive notifications via Slack, email, or GitHub when a performance
          change is detected.
        </p>
      </div>
      <div className="col-sm-4">
        <h3>State of the art</h3>
        <p>
          Change point detection is state of the art technology for detecting
          changes in software performance. Used by leading technology companies
          such all around the world including MongoDB and Netflix.
        </p>
      </div>
    </div>
  );
};

const LearnMore = () => {
  return (
    <div className="container pt-5 text-center">
      <div className="row">
        <h3>Want to learn more?</h3>
        <Link to="/product">Read about the product here</Link>
      </div>
    </div>
  );
};

const FeatureBanner1 = () => {
  return (
    <div className="container-fluid p-5 text-center bg-light">
      <div className="row justify-content-center">
        <div className="col-4 col-4-md text-start align-text-bottom align-self-center">
          <p>
            Even the smallest performance changes can have a big impact on your
            users. Nyrkiö uses change point detection to identify every change
            in your performance data.
          </p>
          <h2>Uncover every performance change</h2>
          <p>
            Change point detection is designed to work with noisy performance
            data which means you can catch every regression and celebrate every
            gain.
          </p>
        </div>
        <div className="col-4 align-items-end justify-content-end">
          <img
            style={{
              width: "80%",
              border: "#efefeb 10px solid",
              borderRadius: "5px",
            }}
            src={tigerbeetle}
            alt="Tigerbeetle change points"
          />
        </div>
      </div>
    </div>
  );
};

const FeatureBanner2 = () => {
  return (
    <div className="container-fluid p-5 text-center bg-nyrkio-dark-red bg-dark">
      <div className="row text-end justify-content-center pt-5">
        <div className="col-4 align-self-center">
          <div className="row text-center">
            <h2>Integrate with your CI/CD</h2>
          </div>
          <div className="row text-start">
            <p>
              Integrate Nyrkiö with your CI/CD pipeline to ensure that
              performance changes are caught before they reach production.
            </p>
            <p>
              It doesn't matter whether you've got end to end tests or
              microbenchmarks. Track metrics as you develop and get notified as
              soon as a change is detected.
            </p>
          </div>
        </div>
        <div className="col-5">
          <img
            style={{
              width: "100%",
              border: "#efefeb 10px solid",
              borderRadius: "5px",
            }}
            src={cicd}
            alt="GitHub commit"
          />
        </div>
      </div>
      <div className="row text-center justify-content-center py-5">
        <div className="col-5 align-items-center">
          <img
            style={{
              width: "100%",
              border: "#efefeb 10px solid",
              borderRadius: "5px",
            }}
            src={commit}
            alt="GitHub commit"
          />
        </div>
        <div className="col-4 text-start align-self-center">
          <h2>Identify the exact commit</h2>
          <p>
            Quickly identity the commit that introduced the performance change
            so the right developer can be notified immediately.
          </p>
          <p>
            With Nyrkiö's GitHub integration there's no need to bisect to find
            the commit that changed performance. One click and you'll know the
            author, the date, and the exact change, reducing the time to fix.
          </p>
        </div>
      </div>
    </div>
  );
};

export const FrontPage = () => {
  return (
    <>
      <div className="container my-5 text-center">
        <Banner />
        <div className="padding-block "></div>
        <FeatureHighlight />
        <button className="btn btn-success">
          <a className="btn-link" href="/signup">
            Sign up
          </a>
        </button>
      </div>
      <div className="padding-block "></div>
      <FeatureBanner1 />
      <div className="padding-block-sm "></div>
      {/* <SampleData /> */}
      {/* <div className="padding-block "></div> */}
      <FeatureBanner2 />
      <LearnMore />
      <></>
    </>
  );
};
