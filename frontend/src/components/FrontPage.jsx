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
import select1before from "../static/runner/turso_select1_ghrunner.png";
import select1after from "../static/runner/turso_select1_nyrkiorunner.png";
import { Slogan, LogoSloganNarrow } from "./Logo";

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
    src="https://www.youtube.com/embed/EKAhgrdERfk?si=TseG4WK67N5pZ1nu"
    title="YouTube video player"
    frameBorder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    referrerPolicy="strict-origin-when-cross-origin"
    allowFullScreen
    ></iframe>
  );
} ;
const FeatureBanner1 = () => {
  return (
    <>
    <div className="container-fluid p-5 text-center">
    <div className="row justify-content-center">
        <h2>Change Point Detection</h2>
        <div className="col-xl-5 col-lg-6 col-sm-12 text-start align-text-bottom align-self-center">
          <p>
            Even the smallest performance changes can have a big impact on your
            users. And if you allow them to compound, your performance risks facing death by a thousand paper cuts...
            </p>
            <p>
            Small 1-5% performance regressions are hard to spot in testing, especially when shifting left to do automatedd testing.
            when the random variation in your benchmarking results is often bigger than that.
          </p>
          <p>
            Nyrkiö uses a state of the art <strong>Change Point Detection</strong> algorithm to identify every change
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

const Mission = () => {
    return (
      <>
      <div className="row w-100 p-2">

      <div className="col-xs-6 nyrkio-runner-title">
      <h3 className="">New:</h3>
      <h1 className="">Nyrkiö Runner for GitHub</h1>
      </div>

      </div>
      <div className="row w-100 p-2">

      <div className="col-xs-12 col-xl-6 text-justify">
      <p>Do you struggle with noisy benchmark results?</p>
      <p>It's hard to spot real regressions if your noise range is 50%, yet this is a common situation for many.</p>
      <p>At Nyrkiö we have a decade of experience how to tune a server for maximum stability and repeatability. Our customers are achieving benchmark results that stay within 1 nanosecond from build to build!</p>
      </div>

      <div className="col-xs-12 col-xl-6 text-justify">
      <img src={select1before} alt="A noisy graph from Nyrkio dashboard" title="Turso SELECT 1 benchmark. Spikes are up to 100 ns, noise range = 40%" style={{maxWidth: "100%"}}/>

      <hr style={{width:"20%", marginLeft:"40%", marginRight:"40%", marginTop: "2em", marginBottom: "2em"}}/>
      </div>

      <div className="col-xs-12 col-xl-6 text-justify">

      <h3><a href="https://github.com/apps/nyrkio/installations/new">1. Install Nyrkiö in your GitHub org >></a></h3>
      <p>Although we support it, we do <strong>NOT</strong> recommend using any 3rd party runners on repositories in your personal GitHub "org", because that requires assigning admin rights to Nyrkiö. Create a separate org and move or clone your repository there.</p>

      <hr style={{width:"20%", marginLeft:"40%", marginRight:"40%", marginTop: "2em", marginBottom: "2em"}}/>

      </div>

      <div className="col-xs-12 col-xl-6 text-justify">
      </div>

      <div className="col-xs-12 col-xl-6 text-justify">
      <h3><a href="/pricing">2. Select a subscription level >></a></h3>

      <p>The first one is consumption based, you only pay for how many minutes you used the servers. Typically less than 10 € / month.</p>

      <hr style={{width:"20%", marginLeft:"40%", marginRight:"40%", marginTop: "2em", marginBottom: "2em"}} />

      </div>

      <div className="col-xs-12 col-xl-6 text-justify">
      </div>

      <div className="col-xs-12 col-xl-6 text-justify">
      <h3 className="nyrkio-accent">3. Choose a runner</h3>
      <p>Lastly: Replace the <span className="gray-bg">runs-on: ubuntu-latest</span> with <span className="gray-bg">runs-on: nyrkio_4</span> </p>
      <p>Your tests will now run on Nyrkiö test runners, and typically you'll see the <span className="nyrkio-accent">noise range in your benchmarks decrease by an order of magnitude!</span></p>
      </div>
      <div className="col-xs-12 col-xl-6 text-justify">
      <img src={select1after} alt="Less noisy graph from Nyrkio dashboard, using Nyrkio runners" title="Turso SELECT 1 benchmark. Variation within 9 ns, noise range = 5%" style={{maxWidth: "100%"}}/>

      <hr style={{width:"20%", marginLeft:"40%", marginRight:"40%", marginTop: "2em", marginBottom: "2em"}}/>
      </div>
      </div>
      </>
    );
};


const OneTwoThree = () => {
  return (
    <>
    <div className="row w-100 p-5 bg-nyrkio-silver">

    <div className="col-xs-12 col-md-6 col-xl-4">
    <h1 className="">What is Nyrkiö, really?</h1>
    </div>
    <div className="col-xs-12 col-md-6 col-xl-8 text-justify">
    <p>Nyrkiö provides tools and server configurations that you can use in your <span className="nyrkio-accent">Continuous Benchmarking workflows.</span></p>

    <p>We provide 4 tools, you can use one or all of them:</p>
    <ol>
    <li><a href="https://github.com/nyrkio/change-detection"><tt>nyrkio/change-detection</tt> GitHub action</a>:<br /> understands the output of the most common benchmark frameworks. It parses your benchmark results, and sends them to nyrkio.com for analysis.</li>
    <li><span className="nyrkio-accent">Nyrkiö Change Detection Service</span>:<br /> Finds performance regressions in your history of continuous benchmarking results. We use a new, state of the art signal processing algorithm that has a low rate of false positives, even in the face of noisy data. Nyrkiö Change Detection Service can also create a GitHub issue or send you a Slack when a regression is found.</li>
    <li><span className="nyrkio-accent">Nyrkiö Runners for GitHub</span>:<br />
    Our GitHub 3rd party runners are configured not for maximum performance but for stable, repeatable performance. Typically you will see a 10x reduction in environmental noise, when compared to the default GitHub runner.</li>
    <li><a href="https://nyrkio.com/docs/git-perf-plugin">git-perf plugin</a><br /> integrates your continuous benchmarking history with <tt>git status</tt>, <tt>git log</tt> and <tt>git blame</tt>.</li>
    </ol>
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
      <img src="/p/NyyrikkiRunner/RunnerBackground-1920-banner2.jpg" style={{
        width: "100%", marginBottom: "2em",
        position: "relative", top: "0px", left: "0px", right: "0px"

      }}/>
      <Slogan />

      {loggedIn? "" :
        (<button className="btn btn-success" style={{position: "relative", top:"-100px", boxShadow: "5px 5px 3px #aaaaaaaa"}}>
        <a className="btn-link" href="/signup">
        Create account &amp; get started
        </a>
        </button>
        )}



          <Mission />
          <OneTwoThree />

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
          <p style={{fontSize: "120%"}}><a href="/product/user-testimonials">Read more about what Nyrkiö users think...</a></p>
          <div className="padding-block-sm "></div>
          <div className="padding-block-sm "></div>
          <p style={{fontSize: "120%"}}>Want more? <a href="/about/ecosystem">Read about how Netflix, Red Hat and Confluent</a> use <strong>change point detection</strong> to stay on top of performance.</p>

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
          <hr />
          <FeatureBanner1 />
          </div>
    </>
  );
};
