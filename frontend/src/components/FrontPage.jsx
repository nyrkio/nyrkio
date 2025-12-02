import { Link } from "react-router-dom";
import { SampleData } from "./SampleData";
import tigerbeetle from "../static/tigerbeetle-change-points.png";
import cicd from "../static/cicd.png";
import commit from "../static/commit.png";
import { Logo } from "./Logo";
import { MyUserCarousel } from "./Carousel";
import { useEffect, useState } from "react";
import AutumnRunner from "../static/AutumnRunner.jpg";
import AutumnRunnerYoutube from "../static/AutumnRunnerYoutube.jpg";

const FeatureHighlight = () => {
  return (
    <>
    <div className="text-center">
      <h2>Continuous Performance Engineering</h2>
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
      src="https://youtube.com/shorts/auZY4_PljWw?si=cva-pBaJ5QhAXWVu"
      title="YouTube video player"
      frameBorder="0"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
      referrerPolicy="strict-origin-when-cross-origin"
      allowFullScreen
    ></iframe>
  );
};

const FeatureBanner1 = () => {
  return (
    <>
    <div className="container-fluid p-5 text-center bg-nyrkio-light-gray">
    <div className="row justify-content-center">
        <h2>Continuous Benchmarking with Confidence</h2>
        <div className="col-xl-5 col-lg-6 col-sm-12 text-start align-text-bottom align-self-center">
          <p>
            Even the smallest performance changes can have a big impact on your
            users. And if you allow them to compound, your performance risks facing death by a thousand paper cuts...
            But small 1-5% performance regressions are hard to spot in testing, especially when shifting left to do automatedd testing.
            when the random variation in your benchmarking results is often bigger than that.
          </p>
          <p>
            Nyrkiö uses <big>Change Point Detection</big> to identify every change
            in your performance data.
            Our change point detection algorithm is designed to work with noisy performance
            data which means you can catch every performance regression, however small or large.
          </p>
          <p>Other similar systems usually catch only the largest performance regressions, 20% or even 50%,
          and even then come with a high false positive rate. Nyrkiö can reliably catch even a 1% regression.
          All automatic, even filing the GitHub issue for you, when a regression was caught.</p>
        </div>

        <div className="col-xl-5 col-lg-6 col-sm-12 align-items-end justify-content-end">
          <img
            style={{
              width: "100%",
              border: "#efefeb 10px solid",
              borderRadius: "5px",
            }}
            src={tigerbeetle}
            alt="TigerBeetle change points"
          />
        </div>
      </div>
    </div>
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
  return (
    <>

      <div className="frontpage container-fluid text-center w-100">

          <div className="text-left coming-soon">
          <a href="https://www.youtube.com/shorts/auZY4_PljWw" target="youtube">
          <img id="idautumnRunnerYoutube" src={AutumnRunnerYoutube} alt="Woman running, red sneakers, autumn leaves" style={{"width": "25%", borderRadius: "15px", boxShadow:"5px 5px 9px #99999999", border: "4px solid #a9988355", position: "absolute", left: "2%", marginRight: "2%", marginBottom: "15em", }} />
          <img id="idautumnRunner" src={AutumnRunner} alt="Woman running, red sneakers, autumn leaves" style={{"width": "25%", borderRadius: "15px", boxShadow:"5px 5px 9px #99999999", border: "4px solid #a9988355", position: "absolute", left: "2%",  marginRight: "2%", marginBottom: "15em", }} />
          </a>

          <h2>Coming soon...</h2>
          <p className=""><em><strong>Nyrkiö runners</strong></em></p>
          <p>Continuous Benchmarking with nanosecond precision!</p>
          <p>Be among the first to hear about it: <br />
          <a href="https://nyrkio.activehosted.com/f/5"><strong>Sign up for our upcoming product news mailing list</strong> &gt;&gt;&gt;</a></p>

          </div>

          <div className="padding-block-sm " style={{clear:"both"}}></div>


          <FeatureBanner1 />

          <div className="padding-block-sm "></div>
          {loggedIn? "" :
            (<button className="btn btn-success">
            <a className="btn-link" href="/signup">
            Create account &amp; get started
            </a>
            </button>
            )}
            <div className="padding-block-sm "></div>

          <div className="user-carousel">
          <h1>What our users say</h1>
          <MyUserCarousel />
          </div>
          <div className="padding-block-sm "></div>
          <p style={{fontSize: "150%"}}><a href="/product/user-testimonials">Read more about what Nyrkiö users think...</a></p>
          <div className="padding-block-sm "></div>
          <div className="padding-block-sm "></div>
          <p style={{fontSize: "150%"}}>Want more? <a href="/about/ecosystem">Read about how Netflix, Red Hat and Confluent</a> use <strong>change point detection</strong> to stay on top of performance.</p>

          <div className="padding-block-sm "></div>
          <div className="padding-block-sm "></div>
          <div className="row">
          <div className="container-fluid text-center col-sm-10 col-md-8 col-lg-8 col-xl-8 nyrkio-public-sample-title  p-3 ">
          <h2>See it for yourself</h2>
          <p>You can browse <em>real, live</em> benchmark results from other Nyrkiö users. The red dots are Change Points reported by Nyrkiö.</p>

          </div>
          </div>
          <SampleData />

          <div className="padding-block "></div>

          <FeatureBanner2 />
          <LearnMore />
        </div>
    </>
  );
};
