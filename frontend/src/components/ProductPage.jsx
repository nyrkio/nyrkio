import tigerbeetle from "../static/tigerbeetle-change-points.png";
import nyrkio_gha from "../static/Nyrkio_GHA.png";
import nyrkio_pr from "../static/NyrkioPrReport.png";
import { LogoBrown } from "./Logo";
import { SampleData } from "./SampleData";
import { GetStartedButton } from "./FrontPage";
import { CpuHours } from "./PricingPage";





export const ProductPage = () => {

  return (
    <>
    <div className="container-fluid w-100">
      <div className="row mt-2 col-xl-10">
      <h1 className="">
          Products
        </h1>
        <p>&nbsp;</p>
        <h4 className="">Nyrkiö develops tools for Continuous Benchmarking</h4>
      </div>
      <div className="row p-2 col-md-10">
        <p>
        Continuous Benchmarking usually consists of the following sub-steps:
        </p>

        <ol>
        <li>
        <img src={nyrkio_gha} alt="Green checkmark as a sign of a passed benchmark on a GitHub pull request" style={{height:"200px", width: "300px", borderRadius: "20px", margin: "2.5em", float: "right"}}/>
        Design one or more benchmarks. Start simple, even one is a great start.
        </li>
        <li>Run the benchmarks <em>continuously</em> in your CI workflows</li>
        <li>Collect results</li>
        <li>Analyze results, and more specifically, find commits that caused performance to degrade</li>
        <li>As needed, assign tickets to the developers who caused a regression</li>
        </ol>


        <p>You are now doing <span className="nyrkio-accent">Continuous Benchmarking</span>.  Congratulations!</p>

        </div>
        <div className="row p-2 col-md-10">
          <div className="col-xs-3 col-lg-4">
          </div>
          <div className="col-xs-6 col-lg-4">
            <GetStartedButton />
          </div>
          </div>
        <div className="row p-2 col-md-10">

        <h2>Nyrkiö Solutions</h2>

        <p>We have over a decade of experience building and analyzing benchmarks and related tools. At Nyrkiö we want to democratize and mainstream that knowledge. We have developed the following tools to help you in each part of this journey.  </p>


        <ol>
        <li>Use the well known framework of the programming language you're working with.*</li>
        <li>Iteratively, as needed, tune your infrastructure, your product, and benchmark tool to minimize environmental noise.
        For best results, Nyrkio offers a 3rd party GitHub runner to run your continuous benchmarks on. We configure these runners NOT for maximum performance, but rather for maximal <span className="nyrkio-accent">stability and repeatability</span>. Using Nyrkiö Runner for GitHub, users typically see a 10x reduction in environmental noise and the [min, max] range of noise below 10 nanoseconds, sometime within 1 nanoseconds!
        </li>
        </ol>

        </div>
        <div className="row p-2 col-md-12 text-center nyrkio-pricing">
          <div className="col-xs-3 col-sm-2">
          </div>
          <div className="col-xs-6 col-sm-6  col-xl-5">
          <CpuHours />
  (See <a href="/pricing">Pricing page for all subscription alternatives</a>)
          </div>
          </div>
        <div className="row p-2 col-md-10">

        <ol start="3">
        <li>The <a href="https://github.com/nyrkio/change-detection?tab=readme-ov-file">nyrkio/change-detection</a> GitHub action knows how to parse the output of the most common benchmarking tools and sends it to nyrkio.com for analysis.</li>
        <li>Nyrkiö <a href="/docs/getting-started">Change Point Detection</a> is the state of the art method for finding regressions (or improvements!)                                                    in noisy benchmarkin results. Our founder is one of the inventors of the method and first in the world to successfully use a change point detection algorithm as part of Continuous Benchmarking, and the first to <a href="https://arxiv.org/abs/2003.00584">publish the results</a> and <a href="https://otava.apache.org">the source code</a>. </li>
        <li>
        Nyrkiö can greate GitHub tickets, or comment on Pull Requests automatically. The ticket is automatically assigned to the commit author.
        <br />
        <img src={nyrkio_pr} alt="PR report with regressions reported, red N logo" style={{height:"300px", width: "700px", borderRadius: "20px", marginBottom: "2.5em", position: "relative", left: "-3.5em", overflow: "clip"}}/>
        </li>
        </ol>


        <p>*) Nyrkiö users also commonly measure and track other values than benchmark results. Or even purely performance related: Size of release files, memory consumption during  a test, etc... A significant change in such metrics is often worth looking into more carefully.</p>


        <p>Read more: <a href="https://blog.nyrkio.com/2025/05/08/welcome-apache-otava-incubating-project/">How we introduced change point detection as a solution to automatically finding regressions in noisy continuous benchmarking test results</a>.</p>
      </div>



        </div>
        <div className="padding-block "></div>
        <div className="row p-2 col-md-10">
          <div className="col-xs-3 col-lg-4">
          </div>
          <div className="col-xs-6 col-lg-4">
            <GetStartedButton />
          </div>
        </div>

      <div className="padding-block "></div>

      <div className="row">
      <div className="container-fluid text-center col-sm-12 col-md-12 col-lg-8 col-xl-8 nyrkio-public-sample-title  p-3 ">

      <h2>See it for yourself</h2>
      <p>
      <br/>
      You can browse <em>real, live</em> benchmark results from other Nyrkiö users. <br />The red dots are Change Points reported by Nyrkiö.</p>
      </div>
      <SampleData />
      </div>
    </>
  );
};
