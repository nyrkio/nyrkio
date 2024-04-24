export const ServicesPage = ({ loggedIn }) => {


  return (
    <>
      <div className="container nyrkio-services">
        <div className="justify-content-center col-xl-12 mt-8 p-5">
            <h1 className="text-center">Services</h1>
            <h2 className="text-center">Change Point Detection related Consulting Services</h2>
            <div className="p-1 mt-4">
              <p>You know you want to improve your automated performance testing, but it's hard to
                 find time to get it done, when there are so many other priorities?</p>
              <p>Creating repeatable, high-fidelity benchmarks for your product can be challenging.
              Why not do a couple first ones together, with experienced performance specialists,
              who've done it before?</p>
              <p>Kickstart your Nyrkiö Platform experience with one of the following packages:</p>
          </div>
        </div>

        <div className="consulting-packages row row-cols-1 row-cols-xl-2 text-center justify-content-center">
          <div className="col">
            <div className="card mb-1 rounded-3 shadow-sm m-1">
              <div className="card-header py-3">
                <h4 className="my-0 fw-normal">Status Check</h4>
              </div>
              <div className="card-body">
                <div className="card-body-text">
                <p>Your starting point</p>
                <ul className="list-unstyled mt-3 mb-4">
                  <li>You know you want to improve your performance testing but don't quite know where to start?</li>
                  <li>You need an assessment of the current state of your performance testing process?</li>
                </ul>
                <p>The engagement</p>
                <ul className="list-unstyled mt-3 mb-4">
                  <li>1 day "check-up" engagement with your performance or QA team, an engineering manager, and a senior performance specialist from Nyrkiö</li>
                  <li>Review your performance testing and compare with modern best practices tools and methods</li>
                  <li>How are results analyzed and what is the mean time to fix regressions?</li>
                  <li>Gap and risk analysis: What is the business impact to you or your customers?</li>
                </ul>
                <p>Deliverables</p>
                <ul className="list-unstyled mt-3 mb-4">
                  <li>A written report with findings on:</li>
                  <li>Holistic overview of your performance engineering process</li>
                  <li>Quality of your current benchmark results: Repeatability, noise, relevance.</li>
                  <li>Suggested improvements</li>
                </ul>
                </div>
                {loggedIn ? (
                  <form
                    action="/api/v0/billing/create-checkout-session"
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
                ) : (
                  <button
                    type="button"
                    className="w-100 btn btn-lg btn-success"
                  >
                    <a className="btn-link" href="/signup">
                      Order online
                    </a>
                  </button>
                )}
                  <button
                    type="button"
                    className="w-100 btn btn-lg btn-success"
                  >
                    <a className="btn-link" href="mailto:sales@nyrkio.com?subject=Order: Performance Status Check">
                      Email us
                    </a>
                  </button>
              </div>
              </div>
            </div>

          <div className="col">
            <div className="card mb-1 rounded-3 shadow-sm m-1">
              <div className="card-header py-3">
                <h4 className="my-0 fw-normal">Change Detection Kickstart</h4>
              </div>
              <div className="card-body">
                <div className="card-body-text">
                <p>Your starting point</p>
                <ul className="list-unstyled mt-3 mb-4">
                  <li>You're already running performance tests regularly</li>
                  <li>You're struggling to analyze results of your nightly performance tests due to too much noise</li>
                  <li>The team is annoyed and/or ignoring benchmark results due to high amount of false positives</li>
                </ul>
                <p>The engagement</p>
                <ul className="list-unstyled mt-3 mb-4">
                  <li>Typically a 1 week engagement to integrate Nyrkiö Change Detection into your existing perf testing workflow</li>
                  <li>1 month follow up period to tune the algorithm for best accuracy and least false positives</li>
                </ul>
                <p>Deliverables</p>
                <ul className="list-unstyled mt-3 mb-4">
                  <li>A working Change Detection and Alerting process</li>
                  <li>State of the are accuracy in automatically identifying which commit introduced a performance regression</li>
                  <li>An engineering team feeling empowered to efficiently detect and fix perf regressions as they happen.</li>
                  <li>A situation where investing in more performance test coverage makes sense as the signal to noise ratio dramatically improved</li>
                </ul>
                <p>Note: Requires a suitable <a href="pricing">Nyrkiö subscription</a>.</p>
                </div>
                {loggedIn ? (
                  <form
                    action="/api/v0/billing/create-checkout-session"
                    method="POST"
                  >
                    <input
                      type="hidden"
                      name="lookup_key"
                      value="services_kickstart"
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
                ) : (
                  <button
                    type="button"
                    className="w-100 btn btn-lg btn-success"
                  >
                    <a className="btn-link" href="/signup">
                      Order online
                    </a>
                  </button>
                )}
                  <button
                    type="button"
                    className="w-100 btn btn-lg btn-success"
                  >
                    <a className="btn-link" href="mailto:sales@nyrkio.com?subject=Order: Nyrkiö Change Detection kickstart">
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

