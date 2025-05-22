import { Link } from "react-router-dom";
import { SampleData } from "./SampleData";
import tigerbeetle from "../static/tigerbeetle-change-points.png";
import cicd from "../static/cicd.png";
import commit from "../static/commit.png";
import { Logo } from "./Logo";
import NyrkioCarousel from "./Carousel";

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
    <div className="container pt-5 text-center">
      <div className="row pt-5">
        <h3>Ready to try it?</h3>
      </div>
      <div className="row pt-2">
        <Link to="/docs/getting-started">Getting started guide</Link>
      </div>
      <div className="row pt-5">
        <h3>Want to learn more?</h3>
      </div>
      <div className="row pt-2">
        <Link to="/product">Read about change detection</Link>
      </div>
    </div>
  );
};

export const DemoVideo = () => {
  return (
    <iframe
      width="933"
      height="525"
      src="https://www.youtube.com/embed/EKAhgrdERfk?si=btV2C2wpDx4d-6lZ"
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
    <div className="container-fluid p-5 text-center bg-light">
      <div className="row justify-content-center">
        <div className="col-md-4 col-sm-12 text-start align-text-bottom align-self-center">
          <p>
            Even the smallest performance changes can have a big impact on your
            users. Nyrkiö uses change point detection to identify every change
            in your performance data.
          </p>
          <h2>Uncover every performance change</h2>
          <p>
            Our change point detection algorithm is designed to work with noisy performance
            data which means you can catch every regression and celebrate every
            gain.
          </p>
        </div>
        <div className="col-md-4 col-sm-12 align-items-end justify-content-end">
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
  );
};

const FeatureBanner2 = () => {
  return (
    <div className="container-fluid p-5 text-center bg-nyrkio-dark-gray bg-dark">
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

export const FrontPage = () => {
  return (
    <>
      <div className="frontpage container-fluid text-center w-100">
        <div className="container-fluid text-center w-100">
          <NyrkioCarousel />
          <div className="padding-block-sm frontpage-triplet"></div>
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
        <SampleData customerName="Turso" customerUrl="https://turso.tech" />
        <div className="padding-block "></div>
        <FeatureBanner2 />
        <LearnMore />
      </div>
    </>
  );
};
