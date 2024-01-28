export const PricingPage = () => {
  return (
    <>
      <div className="container py-3" style={{ maxWidth: "960px" }}>
        <div className="row justify-content-center">
          <div className="p-5 text-center">
            <h1>Pricing</h1>
            <div className="p-3">
              <p>
                Open source projects can get started with the free plan. Or
                select a business or enterprise plan for more features and
                support.
              </p>
            </div>
          </div>
        </div>
        <div className="row row-cols-1 row-cols-md-3 mb-3 text-center justify-content-center">
          <div className="col">
            <div className="card mb-4 rounded-3 shadow-sm">
              <div className="card-header py-3">
                <h4 className="my-0 fw-normal">Free</h4>
              </div>
              <div className="card-body">
                <h1 className="card-title pricing-card-title">
                  €0
                  <small className="text-body-secondary fw-light">/mo</small>
                </h1>
                <ul className="list-unstyled mt-3 mb-4">
                  <li>100 test results</li>
                  <li>1 metric per test</li>
                  <li>Monitor 1 GitHub branch</li>
                </ul>
                <button
                  type="button"
                  className="w-100 btn btn-lg btn-outline-success"
                >
                  Sign up for free
                </button>
              </div>
            </div>
          </div>
          <div className="col">
            <div className="card mb-4 rounded-3 shadow-sm border-success">
              <div className="card-header py-3 border-success">
                <h4 className="my-0 fw-normal">Business</h4>
              </div>
              <div className="card-body">
                <h1 className="card-title pricing-card-title">
                  €200
                  <small className="text-body-secondary fw-light">/mo</small>
                </h1>
                <ul className="list-unstyled mt-3 mb-4">
                  <li>10,000 test results</li>
                  <li>100 metrics per test</li>
                  <li>Email and Slack notifications</li>
                  <li>Support for teams</li>
                </ul>
                <button type="button" className="w-100 btn btn-lg btn-success">
                  Get started
                </button>
              </div>
            </div>
          </div>
          <div className="col">
            <div className="card mb-4 rounded-3 shadow-sm">
              <div className="card-header py-3 text-bg-primary">
                <h4 className="my-0 fw-normal">Enterprise</h4>
              </div>
              <div className="card-body">
                <h1 className="card-title pricing-card-title">Call us</h1>
                <ul className="list-unstyled mt-3 mb-4">
                  <li>Everything in Business, plus...</li>
                  <li>Unlimited results and metrics</li>
                  <li>JIRA integration</li>
                  <li>24/7 support</li>
                </ul>
                <button type="button" className="w-100 btn btn-lg btn-success">
                  <a className="btn-link" href="mailto:founders@nyrk.io">
                    Contact us
                  </a>
                </button>
              </div>
            </div>
          </div>
        </div>

        <h2 className="display-6 text-center mb-4">Compare plans</h2>

        <div className="row">
          <div className="table-responsive">
            <table className="table text-center pricing-table">
              <thead>
                <tr>
                  <th style={{ width: "34%" }}></th>
                  <th style={{ width: "22%" }}>Free</th>
                  <th style={{ width: "22%" }}>Business</th>
                  <th style={{ width: "22%" }}>Enterprise</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th scope="row" className="text-start">
                    Test Results
                  </th>
                  <td>100</td>
                  <td>10,000</td>
                  <td>Unlimited</td>
                </tr>
                <tr>
                  <th scope="row" className="text-start">
                    Metrics per test
                  </th>
                  <td>1</td>
                  <td>100</td>
                  <td>Unlimited</td>
                </tr>
              </tbody>

              <tbody>
                <tr>
                  <th scope="row" className="text-start">
                    GitHub branch monitoring
                  </th>
                  <td>1 branch</td>
                  <td>10 branches</td>
                  <td>Unlimited</td>
                </tr>
                <tr>
                  <th scope="row" className="text-start">
                    GitHub PR gating
                  </th>
                  <td></td>
                  <td>
                    <i className="bi bi-check"></i>
                  </td>
                  <td>
                    <i className="bi bi-check"></i>
                  </td>
                </tr>
                <tr>
                  <th scope="row" className="text-start">
                    GitHub organization support
                  </th>
                  <td></td>
                  <td>
                    <svg className="bi" width="24" height="24">
                      <use xlinkHref="#check" />
                    </svg>
                  </td>
                  <td>
                    <i className="bi bi-check"></i>
                  </td>
                </tr>
                <tr>
                  <th scope="row" className="text-start">
                    Integrations
                  </th>
                  <td></td>
                  <td>Email, Slack</td>
                  <td>Email, Slack, JIRA</td>
                </tr>
                <tr>
                  <th scope="row" className="text-start">
                    Team Size
                  </th>
                  <td>1</td>
                  <td>10</td>
                  <td>Unlimited</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </>
  );
};
