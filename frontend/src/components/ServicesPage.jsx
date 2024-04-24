export const ServicesPage = ({ loggedIn }) => {


  return (
    <>
      <div className="container nyrkio-services">
        <div className="justify-content-center col-xl-12 mt-8 p-5">
            <h1 className="text-center">Services</h1>
            <h2 className="text-center">Change Point Detection related Consulting Services</h2>
            <div className="p-3 mb-3">
              <p>You know you want to improve your automated performance testing, but it's hard to
                 find time to get it done, when there are so many other priorities?</p>
              <p>Creating repeatable, high-fidelity benchmarks for your product can be challenging.
              Why not do a couple first ones together, with experienced performance specialists,
              who've done it before?</p>
              <p>Kickstart your Nyrkiö Platform experience with one of the following packages:</p>
          </div>
        </div>

        <div className="consulting-packages row row-cols-1 row-cols-lg-2 text-center justify-content-center">
          <div className="col">
            <div className="card mb-4 rounded-3 shadow-sm m-4">
              <div className="card-header py-3">
                <h4 className="my-0 fw-normal">Status Check</h4>
              </div>
              <div className="card-body">
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
          </div>

        </div>
    </>
  );
};

