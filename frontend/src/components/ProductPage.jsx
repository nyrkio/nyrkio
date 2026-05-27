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
    <div className="container">
      <h1 className="text-primary text-center">Products</h1>
      <div className="row align-items-center mt-4">
        <div className="col-md-6">
          <h2 className="h3 ">Nyrkiö develops tools for Continuous Benchmarking</h2>
          <p>
            <b className="text-secondary">Continuous Benchmarking usually consists of the following sub-steps:</b>
            <ol>
              <li>Design one or more benchmarks. Start simple, even one is a great start.</li>
              <li>Run the benchmarks <em>continuously</em> in your CI workflows</li>
              <li>Collect results</li>
              <li>Analyze results, and more specifically, find commits that caused performance to degrade</li>
              <li>As needed, assign tickets to the developers who caused a regression</li>
            </ol>
          </p>
        </div>
        <div class="col-md-6 text-md-end">
          <img className="img-fluid border border-2 border-secondary rounded shadow p-3" width="422" height="280" src={nyrkio_gha} alt="Green checkmark as a sign of a passed benchmark on a GitHub pull request"/>
        </div>
      </div>
      <p className="text-center my-5 fw-semibold text-secondary">You are now doing <span className="nyrkio-accent">Continuous Benchmarking</span>.  Congratulations!</p>
      <div className="d-flex flex-column flex-md-row gap-2 gap-md-4 justify-content-center mb-4 mb-md-7">
        <GetStartedButton />
        <a className="btn btn-outline-primary" href="/public">Public Test Results</a>
      </div>

      <h2 className="h3 text-center text-secondary">Nyrkiö Solutions</h2>
      <p className="text-center text-secondary fw-semibold">
        We have over a decade of experience building and analyzing benchmarks and related tools. At Nyrkiö we want to democratize and mainstream that knowledge. <br className="d-none d-md-block" />
        We have developed the following tools to help you in each part of this journey.
      </p>

      <ol>
        <li className="mb-4">
          Use the well known framework of the programming language you're working with.*
        </li>
        <li className="mb-3">
          Iteratively, as needed, tune your infrastructure, your product, and benchmark tool to minimize environmental noise. For best results, Nyrkio offers a 3rd party GitHub runner to run your continuous benchmarks on. We configure these runners NOT for maximum performance, but rather for maximal <span className="nyrkio-accent">stability and repeatability</span>. Using Nyrkiö Runner for GitHub, users typically see a 10x reduction in environmental noise and the [min, max] range of noise below 10 nanoseconds, sometime within 1 nanoseconds!
          <div className="d-flex justify-content-center mt-4">
            <CpuHours />
          </div>
          <div className="text-center">
            <a className="btn btn-outline-primary mt-4 mt-md-6 mb-4" href="/pricing">All Pricing</a>
          </div>
        </li>
        <li className="mb-3">
          The <a href="https://github.com/nyrkio/change-detection?tab=readme-ov-file">nyrkio/change-detection</a> GitHub action knows how to parse the output of the most common benchmarking tools and sends it to nyrkio.com for analysis.
        </li>
        <li className="mb-3">
          Nyrkiö <a href="/docs/getting-started">Change Point Detection</a> is the state of the art method for finding regressions (or improvements!) in noisy benchmarkin results. Our founder is one of the inventors of the method and first in the world to successfully use a change point detection algorithm as part of Continuous Benchmarking, and the first to <a href="https://arxiv.org/abs/2003.00584">publish the results</a> and <a href="https://otava.apache.org">the source code</a>.
        </li>
        <li className="mb-3">
          Nyrkiö can greate GitHub tickets, or comment on Pull Requests automatically. The ticket is automatically assigned to the commit author.
          <div className="d-flex justify-content-center my-4">
            <img width="1393" height="683" className="w-md-75 w-xxl-50 img-fluid border border-2 border-secondary rounded shadow p-3" src={nyrkio_pr} alt="PR report with regressions reported, red N logo"/>
          </div>
        </li>
      </ol>


      <p className="text-center">*) Nyrkiö users also commonly measure and track other values than benchmark results. Or even purely performance related: Size of release files, memory consumption during  a test, etc... A significant change in such metrics is often worth looking into more carefully.</p>


      <p className="text-center">Read more: <a href="https://blog.nyrkio.com/2025/05/08/welcome-apache-otava-incubating-project/">How we introduced change point detection as a solution to automatically finding regressions in noisy continuous benchmarking test results</a>.</p>
      <div className="d-flex flex-column flex-md-row gap-2 gap-md-4 justify-content-center my-4">
        <GetStartedButton />
        <a className="btn btn-outline-primary" href="https://blog.nyrkio.com/">Blog</a>
      </div>
      <hr className="mt-4 mt-md-6"/>
      </div>
      <SampleData />
    </>
  );
};
