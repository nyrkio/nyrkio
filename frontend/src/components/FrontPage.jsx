import { Link } from "react-router-dom";
import { SampleData } from "./SampleData";
import tigerbeetle from "../static/tigerbeetle-change-points.png";
import cicd from "../static/cicd.png";
import commit from "../static/commit.png";
import { Logo } from "./Logo";
import { MyUserCarousel } from "./Carousel";
import { useEffect, useState } from "react";
import fosdembar from "../static/9174011399_3d91025136_c.jpg";
import stickers from "../static/stickers.png";
import { HeroBanner } from "./HeroBanner/HeroBanner.jsx";
import { Mission } from "./Mission/Mission.jsx";
import Reviews from "./Review/Reviews.jsx";
import WhatMore from "./WhatMore/WhatMore.jsx";

const FeatureHighlight = () => {
  return (
    <>
    <div className="text-center">
      <h2>Continuous Benchmarking</h2>
    </div>
    <div className="row row-cols-lg-3 row-cols-1 frontpage-triplet text-center m-5">
      <div className="col">
        <h3>1. Automate benchmarking</h3>
        <p>
          Performance regressions are often only discovered during later stages
          of development such as release candidate testing.
        </p>
        <p>
          Pull your performance testing earlier with Nyrkiö and flag regressions
          as soon as they're committed.
        </p>
      </div>
      <div className="col">
        <h3>2. Automate analysis</h3>
        <p>
          Avoid the tedious work of checking performance dashboards by hand.
          Let Nyrkiö send notifications via Slack, email, or GitHub when a performance
          change is detected.
        </p>
      </div>
      <div className="col">
        <h3>3. Math is hard</h3>
        <p>
          ...but we got you covered!<br />
          Going crazy with too many false positives?<br />
          Nyrkiö Change Point Detection is state of the art technology for detecting
          regressions in software performance. Used by leading technology companies
          around the world, including MongoDB and Netflix, and based on open source Apache Otava&TM; (Incubating).
        </p>
      </div>
    </div>
    </>
  );
};

const LearnMore = () => {
  return (
    <div className="row pt-5 text-center">
      <div className="col-xs-12 col-md-3">
        <h3>Ready to try it?</h3>
        <Link to="/docs/getting-started">Getting started guide</Link>
      </div>
      <div className="col-xs-12 col-md-3">
        <h3>Want to learn more?</h3>
        <Link to="/product">Read about how it works</Link>
      </div>
      <div className="col-xs-12 col-md-3">
        <h3>Need help?</h3>
        <Link to="/services">We offer consulting packages to get you started. </Link>
      </div>
        <div className="col-xs-12 col-md-3">
          <h3>Get involved!</h3>
          <Link to="/about/ecosystem">Open Source Ecosystem </Link>
        </div>
      </div>
  );
};

export const DemoVideo = () => {
  return (
    <iframe
    id="demo-video"
    style={{maxWidth: "90%", maxHeight: "90%", minWidth: "360px", minHeight: "360px"}}
    src="https://www.youtube.com/embed/EKAhgrdERfk?si=TseG4WK67N5pZ1nu"
    title="YouTube video player"
    frameBorder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    referrerPolicy="strict-origin-when-cross-origin"
    allowFullScreen
    ></iframe>
  );
} ;
const ChangePointDetection = () => {
  return (
    <>
      <section className="container mt-section">
        <h2 className="text-center text-primary mb-4">Change Point Detection</h2>
        <div className="rounded-3 shadow p-4" style={{backgroundColor: '#FFFDE5'}}>
          <div className="row align-items-center">
            <div className="col-12 col-lg-6 mb-4 mb-lg-0 order-lg-last">
              <div className="rounded-3 border border-primary shadow bg-white p-3">
                <img
                  className="img-fluid"
                  src={tigerbeetle}
                  alt="TigerBeetle change points"
                  width="1801"
                  height="602"
                />
              </div>
            </div>
            <div className="col-12 col-lg-6">
              <p className="mb-3 mb-lg-5">
                Even the smallest performance changes can have a big impact on your
                users. And if you allow them to compound, your performance risks facing death by a thousand paper cuts...
              </p>
              <p className="mb-3 mb-lg-5">
                Small 1-5% performance regressions are hard to spot in testing, especially when shifting left to do automatedd testing.
                when the random variation in your benchmarking results is often bigger than that.
              </p>
              <p className="mb-3 mb-lg-5">
                Nyrkiö uses a state of the art <strong className="text-secondary">Change Point Detection</strong> algorithm to identify every change
                in your performance data.
                Our change point detection algorithm is designed to work with noisy performance
                data which means you can catch every performance regression, however small or large.
              </p>
              <p className="mb-3 mb-lg-5">Other similar systems usually catch only the largest performance regressions, 20% or even 50%,
                and even then come with a high false positive rate. Nyrkiö can reliably catch even a 1% regression.
                All automatic, even filing the GitHub issue for you, when a regression was caught.</p>
            </div>
          </div>
        </div>
      </section>
    </>
  );
};


const OneTwoThree = ({loggedIn}) => {
  return (
    <>
      <section className="py-section" style={{backgroundColor: '#FFFDE5'}}>
        <div className="container">
          <div className="row align-items-center">
            <div className="col-xs-12 col-lg-6 col-xl-5 pe-xl-7">
              <h2 className="text-primary mb-4">What is Nyrkiö, really?</h2>
              <p>Nyrkiö provides tools and server configurations that you can use in your <strong className="text-secondary">Continuous Benchmarking workflows</strong></p>
            </div>
            <div className="col-xs-12 col-lg-6 col-xl-7 text-justify">
              <h3 className="text-secondary h6 fw-semibold mb-4">We provide 4 tools, you can use one or all of them:</h3>
              <h4 className="text-primary h6">1. <a href="https://github.com/nyrkio/change-detection"><tt>nyrkio/change-detection</tt> GitHub action:</a></h4>
              <p>Understands the output of the most common benchmark frameworks. It parses your benchmark results, and sends them to nyrkio.com for analysis.</p>
              <h4 className="text-primary h6">2. <a href="/docs/getting-started">Nyrkiö Change Detection Service:</a></h4>
              <p>Finds performance regressions in your history of continuous benchmarking results. We use a new, state of the art signal processing algorithm that has a low rate of false positives, even in the face of noisy data. Nyrkiö Change Detection Service can also create a GitHub issue or send you a Slack when a regression is found.</p>
              <h4 className="text-primary h6">3. Nyrkiö Runners for GitHub:</h4>
              <p>Our GitHub 3rd party runners are configured not for maximum performance but for stable, repeatable performance. Typically you will see a 10x reduction in environmental noise, when compared to the default GitHub runner.</p>
              <h4 className="text-primary h6">4. <a href="https://nyrkio.com/docs/git-perf-plugin">git-perf plugin</a></h4>
              <p>Integrates your continuous benchmarking history with <tt>git status</tt>, <tt>git log</tt> and <tt>git blame</tt>.</p>
              {!loggedIn && (<a className="btn btn-primary mt-4 d-block d-md-inline-block" href="/signup">Create account &amp; get started</a>)}
            </div>
          </div>
        </div>
      </section>
    </>
  );
};


const FeatureBanner2 = () => {
  return (
    <div className="container-fluid p-5 text-center bg-nyrkio-light-gray">
      <div className="row text-end justify-content-center pt-5">
        <div className="col-md-4 col-sm-12 align-self-center">
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
        <div className="col-md-5 col-sm-12">
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
        <div className="col-md-5 col-sm-12 align-items-center">
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
        <div className="col-md-4 col-sm-12 text-start align-self-center pt-3">
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

export const FrontPage = ({loggedIn}) => {
  document.body.classList.add("section-front");
  document.body.classList.remove("section-dashboard");
  return (
    <>
      <div className="frontpage page-wrapper">
        <HeroBanner cta={{
          access: !loggedIn,
          title: 'Create account &amp; get started',
          url: '/signup',
        }} />
        <Mission loggedIn={loggedIn} />
        <OneTwoThree loggedIn={loggedIn} />
        <Reviews />
        <WhatMore />
        <SampleData />

        <ChangePointDetection />
        </div>
    </>
  );
};

export const GetStartedButton = ({loggedIn}) => {
  if (loggedIn) {
    return "";
  }

  return (<a className="btn btn-primary" href="/signup">Create account &amp; get started</a>)
};


const GetStartedButtonUp = ({loggedIn}) => {
  if (loggedIn){
    return "";
  }

  return (<button className="btn btn-success" style={{position: "relative", top:"-200px", boxShadow: "5px 5px 3px #aaaaaaaa"}}>
  <a className="btn-link" href="/signup">
  Create account &amp; get started
  </a>
  </button>
  )
};


