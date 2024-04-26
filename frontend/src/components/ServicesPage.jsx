export const ServicesPage = ({ loggedIn }) => {
  return (
    <>
      <div className="container nyrkio-services">
        <div className="justify-content-center col-xl-12 mt-8 p-5">
          <h1 className="text-center">Services</h1>
          <h2 className="text-center">
            Change Point Detection related Consulting Services
          </h2>
          <div className="p-1 mt-4">
            <p>
              You know you want to improve your automated performance testing,
              but it's hard to find time to get it done, when there are so many
              other priorities?
            </p>
            <p>
              Creating repeatable, high-fidelity benchmarks for your product can
              be challenging. Why not do a couple first ones together, with
              experienced performance specialists, who've done it before?
            </p>
            <p>
              Kickstart your Nyrkiö Platform experience with one of the
              following packages:
            </p>
          </div>
        </div>

        <div className="consulting-packages row row-cols-1 row-cols-xl-2 row-cols-xxl-3">
          <div className="col">
            <div className="card mb-1 rounded-3 shadow-sm m-2 text-center justify-content-center">
              <div className="card-header py-3">
                <h4 className="my-0 fw-normal">Status Check</h4>
              </div>
              <div className="card-body">
                <div className="card-body-text">
                  <p>Your starting point</p>
                  <ul className="list-unstyled mt-3 mb-4">
                    <li>
                      You know you want to improve your performance testing but
                      don't quite know where to start?
                    </li>
                    <li>
                      You need an assessment of the current state of your
                      performance testing process?
                    </li>
                  </ul>
                  <p>The engagement</p>
                  <ul className="list-unstyled mt-3 mb-4">
                    <li>
                      1 day "check-up" engagement with your performance or QA
                      team, an engineering manager, and a senior performance
                      specialist from Nyrkiö
                    </li>
                    <li>
                      Review your performance testing and compare with modern
                      best practices tools and methods
                    </li>
                    <li>
                      How are results analyzed and what is the mean time to fix
                      regressions?
                    </li>
                    <li>
                      Gap and risk analysis: What is the business impact to you
                      or your customers?
                    </li>
                  </ul>
                  <p>Deliverables</p>
                  <ul className="list-unstyled mt-3 mb-4">
                    <li>A written report with findings on:</li>
                    <li>
                      Holistic overview of your performance engineering process
                    </li>
                    <li>
                      Quality of your current benchmark results: Repeatability,
                      noise, relevance.
                    </li>
                    <li>Suggested improvements</li>
                  </ul>
                  <p>Price: €2400</p>
                </div>
                <form
                  action="/api/v0/billing/create-checkout-session?mode=payment"
                  method="POST"
                >
                  <input
                    type="hidden"
                    name="lookup_key"
                    value="services_status_check"
                  />
                  <input type="hidden" name="quantity" value={2400} />
                  <button
                    id="checkout-and-portal-button"
                    type="submit"
                    className="w-100 btn btn-lg btn-success"
                  >
                    Order online
                  </button>
                </form>
                <button type="button" className="w-100 btn btn-lg btn-success">
                  <a
                    className="btn-link"
                    href="mailto:sales@nyrkio.com?subject=Order: Performance Status Check"
                  >
                    Email us
                  </a>
                </button>
              </div>
            </div>
          </div>

          <div className="col">
            <div className="card mb-1 rounded-3 shadow-sm m-2 text-center justify-content-center">
              <div className="card-header py-3">
                <h4 className="my-0 fw-normal">Change Detection Kickstart</h4>
              </div>
              <div className="card-body">
                <div className="card-body-text">
                  <p>Your starting point</p>
                  <ul className="list-unstyled mt-3 mb-4">
                    <li>You're already running performance tests regularly</li>
                    <li>
                      You're struggling to analyze results of your nightly
                      performance tests due to too much noise
                    </li>
                    <li>
                      The team is annoyed and/or ignoring benchmark results due
                      to high amount of false positives
                    </li>
                  </ul>
                  <p>The engagement</p>
                  <ul className="list-unstyled mt-3 mb-4">
                    <li>
                      Typically a 1 week engagement to integrate Nyrkiö Change
                      Detection into your existing perf testing workflow
                    </li>
                    <li>
                      1 month follow up period to tune the algorithm for best
                      accuracy and least false positives
                    </li>
                  </ul>
                  <p>Deliverables</p>
                  <ul className="list-unstyled mt-3 mb-4">
                    <li>A working Change Detection and Alerting process</li>
                    <li>
                      State of the are accuracy in automatically identifying
                      which commit introduced a performance regression
                    </li>
                    <li>
                      An engineering team feeling empowered to efficiently
                      detect and fix perf regressions as they happen.
                    </li>
                    <li>
                      A situation where investing in more performance test
                      coverage makes sense as the signal to noise ratio
                      dramatically improved
                    </li>
                  </ul>
                  <p>Price: €9600</p>
                  <p>
                    Note: Requires a suitable{" "}
                    <a href="pricing">Nyrkiö subscription</a>.
                  </p>
                </div>
                <form
                  action="/api/v0/billing/create-checkout-session?mode=payment"
                  method="POST"
                >
                  <input
                    type="hidden"
                    name="lookup_key"
                    value="services_kickstart"
                  />
                  <input type="hidden" name="quantity" value={9600} />
                  <button
                    id="checkout-and-portal-button"
                    type="submit"
                    className="w-100 btn btn-lg btn-success"
                  >
                    Order online
                  </button>
                </form>
                <button type="button" className="w-100 btn btn-lg btn-success">
                  <a
                    className="btn-link"
                    href="mailto:sales@nyrkio.com?subject=Order: Nyrkiö Change Detection kickstart"
                  >
                    Email us
                  </a>
                </button>
              </div>
            </div>
          </div>

          <div className="col">
            <div className="card mb-1 rounded-3 shadow-sm m-2 text-center justify-content-center">
              <div className="card-header py-3">
                <h4 className="my-0 fw-normal">Automated Benchmarking</h4>
              </div>
              <div className="card-body">
                <div className="card-body-text">
                  <p>Your starting point</p>
                  <ul className="list-unstyled mt-3 mb-4">
                    <li>
                      You're not yet running benchmarks automated, as part of
                      Continuous Integration workflow
                    </li>
                    <li>
                      You risk delayed releases or unhappy customers when
                      performance regressions are released into production
                    </li>
                  </ul>
                  <p>The engagement</p>
                  <ul className="list-unstyled mt-3 mb-4">
                    <li>2-12 weeks, based on initial scoping interview</li>
                    <li>
                      A Nyrkiö performance expert will implement your first
                      benchmark(s)
                    </li>
                    <li>
                      Make the benchmarks run automatically as part of your CI,
                      using elastic cloud infrastructure
                    </li>
                    <li>
                      Configure the benchmark infrastructure for minimal noise,
                      maximum repeatability
                    </li>
                    <li>Analyze results with Nyrkiö Change Detection</li>
                    <li>
                      Configure automated alerting (Slack or Email) in case
                      performance regressions are detected
                    </li>
                  </ul>
                  <p>Deliverables</p>
                  <ul className="list-unstyled mt-3 mb-4">
                    <li>A working perf testing workflow of nightly builds</li>
                    <li>
                      One or more benchmarks relevant to your end user workloads
                    </li>
                  </ul>
                  <p>
                    Note: Requires a suitable{" "}
                    <a href="pricing">Nyrkiö subscription</a>.
                  </p>
                </div>
                <button
                  htmlstyle="background-color: white;"
                  type="button"
                  className="w-100 btn btn-lg btn-success disabled-empty-space"
                >
                  <a
                    className="btn-link"
                    href="."
                    htmlstyle="background-color: white;"
                  >
                    X
                  </a>
                </button>
                <button type="button" className="w-100 btn btn-lg btn-success">
                  <a
                    className="btn-link"
                    href="mailto:sales@nyrkio.com?subject=Order: Nyrkiö Automated Benchmarking Introduction"
                  >
                    Email us
                  </a>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="justify-content-center col-xl-12 mt-8 p-5">
          <h2 className="text-center">
            General Performance and Test Automation
          </h2>
          <div className="p-1 mt-4">
            <p>
              We have deep experience diagnosing and fixing complex scaling
              problems found in distributed systems.
            </p>
            <p>The following are examples of consulting we have delivered:</p>
          </div>
        </div>

        <div className="consulting-packages row row-cols-1 row-cols-xl-2 row-cols-xxl-3">
          <div className="col">
            <div className="card mb-1 rounded-3 shadow-sm m-2 text-center justify-content-center">
              <div className="card-header py-3">
                <h4 className="my-0 fw-normal">
                  Analyze &amp; Fix Perf problems
                </h4>
              </div>
              <div className="card-body">
                <div className="card-body-text">
                  <p>Your starting point</p>
                  <ul className="list-unstyled mt-3 mb-4">
                    <li>
                      Your customer has reported an issue with performance,
                      scaling, or similar
                    </li>
                    <li>
                      You and your team are struggling to find the root cause;
                      or...
                    </li>
                    <li>
                      The problem is in a component or programming language your
                      team doesn't have the required competence in
                    </li>
                    <li>
                      You are losing deals or renewals due to performance and
                      need to improve quickly
                    </li>
                  </ul>
                  <p>The engagement</p>
                  <ul className="list-unstyled mt-3 mb-4">
                    <li>
                      Typically time and materials based engagement with your
                      team to help analyze and fix the reported problem
                    </li>
                  </ul>
                  <p>Deliverables</p>
                  <ul className="list-unstyled mt-3 mb-4">
                    <li>A patch or Pull Request that resolves the issue</li>
                    <li>
                      Producing a new release of your product that includes the
                      fix, is out of scope for the engagement
                    </li>
                    <li>
                      Upgrading and supporting systems at your end customer is
                      likewise out of scope for the engagement
                    </li>
                  </ul>
                </div>
                <button type="button" className="w-100 btn btn-lg btn-success">
                  <a
                    className="btn-link"
                    href="mailto:sales@nyrkio.com?subject=Order: Performance Status Check"
                  >
                    Email us
                  </a>
                </button>
              </div>
            </div>
          </div>

          <div className="col">
            <div className="card mb-1 rounded-3 shadow-sm m-2 text-center justify-content-center">
              <div className="card-header py-3">
                <h4 className="my-0 fw-normal">Faster CI</h4>
              </div>
              <div className="card-body">
                <div className="card-body-text">
                  <p>Your starting point</p>
                  <ul className="list-unstyled mt-3 mb-4">
                    <li>Your Automated testing is taking hours</li>
                    <li>
                      This hurts productivity as developers are frequently
                      waiting for tests to complete
                    </li>
                  </ul>
                  <p>The engagement</p>
                  <ul className="list-unstyled mt-3 mb-4">
                    <li>
                      We work on making your testing faster, or parallelizing
                      your CI workflow, so that the total runtime is shortened.
                    </li>
                  </ul>
                  <p>Deliverables</p>
                  <ul className="list-unstyled mt-3 mb-4">
                    <li>
                      A typical goal might be to cut your build completion time
                      in half
                    </li>
                    <li>
                      Alternatively we can agree on a specific goal, like 30 or
                      60 minutes
                    </li>
                  </ul>
                </div>
                <button type="button" className="w-100 btn btn-lg btn-success">
                  <a
                    className="btn-link"
                    href="mailto:sales@nyrkio.com?subject=Order: Faster CI"
                  >
                    Email us
                  </a>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};
