import { useEffect, useState } from "react";
import { DemoVideo } from "./FrontPage";

export const PricingPage = ({ loggedIn }) => {
  const b = 200;
  const e = 500;
  const [businessPrice, setBusinessPrice] = useState(b);
  const [enterprisePrice, setEnterprisePrice] = useState(e);
  const [annualDiscount, setAnnualDiscount] = useState(false);
  const [annualSavingsPercent, setAnnualSavingsPercent] = useState(20);
  const [bannualSavingsEuro, setBannualSavingsEuro] = useState(
    b * 12 * (annualSavingsPercent / 100)
  );
  const [annualSavingsEuro, setAnnualSavingsEuro] = useState(
    e * 12 * (annualSavingsPercent / 100)
  );
  const [busYear, setBusYear] = useState(b * 12);
  const [entYear, setEntYear] = useState(e * 12);


  const updateDiscount = () => {
    const widget = document.getElementById("flexSwitchAnnual");
    if (widget) {
      setAnnualDiscount(widget.checked);
    }
  };

  const BusinessPrice = () => {
    if (annualDiscount) {
      return (
        <>
          {businessPrice * 12 * (1 - annualSavingsPercent / 100)}{" "}
          <small className="text-body-secondary fw-light"> €/yr</small>
        </>
      );
    } else {
      return (
        <>
          {businessPrice}{" "}
          <small className="text-body-secondary fw-light"> €/mo</small>
        </>
      );
    }
  };

  const EnterprisePrice = () => {
    if (enterprisePrice === null) {
      return <>Call us</>;
    }
    if (annualDiscount) {
      return (
        <>
          {enterprisePrice * 12 * (1 - annualSavingsPercent / 100)}{" "}
          <small className="text-body-secondary fw-light"> €/yr</small>
        </>
      );
    } else {
      return (
        <>
          {enterprisePrice}{" "}
          <small className="text-body-secondary fw-light"> €/mo</small>
        </>
      );
    }
  };



  return (
    <>
      <div
        className="nyrkio-pricing container py-3"
        style={{ maxWidth: "960px" }}
      >
        <div className="container-fluid justify-content-center text-center w-100">
          <h1>Pricing</h1>
        </div>


        <div className="nyrkio-plans row row-cols-1 row-cols-lg-3 text-center justify-content-center">
          <div className="col">
            <div className="card mb-4 rounded-3 shadow-sm m-4">
              <div className="card-header py-3">
                <h4 className="my-0 fw-normal">Free</h4>
              </div>
              <div className="card-body">
                <h1 className="card-title pricing-card-title">
                  0<small className="text-body-secondary fw-light"> €/mo</small>
                </h1>
                <ul className="list-unstyled mt-3 mb-4">
                  <li>1 Git branch</li>
                  <li>10 tests per branch</li>
                  <li>10 metrics per test</li>
                  <li>History of 100 points per metric</li>
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
            <div className="card mb-4 rounded-3 shadow-sm border-success m-4">
              <div className="card-header py-3">
                <h4 className="my-0 fw-normal">Business</h4>
              </div>
              <div className="card-body">
                <p className="nyrkio-annual">{busYear}</p>
                <h1 className="card-title pricing-card-title">
                  <BusinessPrice />
                </h1>
                <ul className="list-unstyled mt-3 mb-4">
                  <li>1 Git repository</li>
                  <li>10 Git branches</li>
                  <li>200 points per metric</li>
                  <li>Email and Slack notifications</li>
                  <li>Support for teams</li>
                </ul>
                {loggedIn ? (
                  <form
                    action="/api/v0/billing/create-checkout-session?mode=subscription"
                    method="POST"
                  >
                    <input
                      type="hidden"
                      name="lookup_key"
                      value={
                        annualDiscount ? "simple_business_yearly" : "simple_business_monthly"
                      }
                    />
                    <input type="hidden" name="quantity" value="1" />
                    <button
                      id="checkout-and-portal-button-business"
                      type="submit"
                      className="w-100 btn btn-lg btn-success"
                      onClick={(e) => {
                        if (total <= 0) {
                          alert(
                            "Please enter number of employees in the company."
                          );
                          e.preventDefault();
                          return false;
                        }
                      }}
                    >
                      Get started
                    </button>
                  </form>
                ) : (
                  <button
                    type="button"
                    className="w-100 btn btn-lg btn-success"
                  >
                    <a className="btn-link" href="/signup">
                      Sign up
                    </a>
                  </button>
                )}
              </div>
            </div>
          </div>

          <div className="col">
            <div className="card mb-4 rounded-3 shadow-sm m-4">
              <div className="card-header py-3 text-bg-primary">
                <h4 className="my-0 fw-normal">Enterprise</h4>
              </div>
              <div className="card-body">
                <p className="nyrkio-annual">{entYear}</p>
                <h1 className="card-title pricing-card-title">
                  <EnterprisePrice />
                </h1>
                <ul className="list-unstyled mt-3 mb-4">
                  <li>10 Git repositories</li>
                  <li>Unlimited branches and metrics</li>
                  <li>JIRA integration</li>
                  <li>Email and Slack notifications</li>
                  <li>Support for teams</li>
                </ul>
                {loggedIn ? (
                  <form
                    action="/api/v0/billing/create-checkout-session?mode=subscription"
                    method="POST"
                  >
                    <input
                      type="hidden"
                      name="lookup_key"
                      value={
                        annualDiscount
                          ? "simple_enterprise_yearly"
                          : "simple_enterprise_monthly"
                      }
                    />
                    <input type="hidden" name="quantity" value="1" />
                    <button
                      id="checkout-and-portal-button-enterprise"
                      type="submit"
                      className="w-100 btn btn-lg btn-success"
                    >
                      Get started
                    </button>
                  </form>
                ) : (
                  <button
                    type="button"
                    className="w-100 btn btn-lg btn-success"
                  >
                    <a className="btn-link" href="/signup">
                      Sign up
                    </a>
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="p-5 pt-2 pb-4 m-5 calculator-annual rounded-3 shadow-sm">
          <div className="row">
            <div className="col col-xs-8" id="annual_discount_label">
              <div className="form-check form-switch">
                <input
                  className="form-check-input"
                  type="checkbox"
                  role="switch"
                  id="flexSwitchAnnual"
                  onChange={updateDiscount}
                />
                <label className="form-check-label" htmlFor="flexSwitchAnnual">
                  Save {bannualSavingsEuro} € or {annualSavingsEuro} € ({annualSavingsPercent} %) by paying for the full year up front!
                </label>
              </div>
            </div>
          </div>
        </div>

        <div className="container-fluid justify-content-center text-center w-100">
          <DemoVideo />
        </div>
        <h2 className="display-6 text-center mb-4 nyrkio-compare-plans">
          Compare plans
        </h2>

        <div className="row">
          <div className="table-responsive">
            <table className="table text-center pricing-table">
              <thead>
                <tr>
                  <th style={{ width: "30%" }}></th>
                  <th style={{ width: "20%" }}>Free</th>
                  <th style={{ width: "20%" }}>Business</th>
                  <th style={{ width: "20%" }}>Enterprise</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th scope="row" className="text-start">
                    GitHub repositories
                  </th>
                  <td>1</td>
                  <td>1</td>
                  <td>10</td>
                </tr>
                <tr>
                  <th scope="row" className="text-start">
                    GitHub branches
                  </th>
                  <td>1</td>
                  <td>10</td>
                  <td>Unlimited</td>
                </tr>
                <tr>
                  <th scope="row" className="text-start">
                    Tests / branch
                  </th>
                  <td>10</td>
                  <td>Unlimited</td>
                  <td>Unlimited</td>
                </tr>
                <tr>
                  <th scope="row" className="text-start">
                    Metrics / test
                  </th>
                  <td>10</td>
                  <td>Unlimited</td>
                  <td>Unlimited</td>
                </tr>
                <tr>
                  <th scope="row" className="text-start">
                    History of points / metric
                  </th>
                  <td>100</td>
                  <td>200</td>
                  <td>Unlimited</td>
                </tr>
              </tbody>

              <tbody></tbody>

              <tbody>
                <tr>
                  <th scope="row" className="text-start">
                    GitHub PR gating
                  </th>
                  <td>
                    <i className="bi bi-check"></i>
                  </td>
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
                    <i className="bi bi-check"></i>
                  </td>
                  <td>
                    <i className="bi bi-check"></i>
                  </td>
                </tr>
                <tr>
                  <th scope="row" className="text-start">
                    Slack alerts
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
                    Email alerts
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
                    Jira integration
                  </th>
                  <td></td>
                  <td></td>
                  <td>
                    <i className="bi bi-check"></i>
                  </td>
                </tr>
              </tbody>


            </table>
          </div>
        </div>
        <div className="row nyrkio-open-source">
          <div className="text-center">
            <h3>Open Source projects apply here...</h3>
            <div className="p-3 mb-3">
              We have a limited capacity, but whenever possible, we offer free
              Business subscriptions to Open Source projects. If you're
              interested, <a href="mailto:helloworld@nyrkio.com">email us!</a>
            </div>
          </div>
        </div>
      </div>
      <div style={{opacity: 0.2}} >
      {loggedIn ? (
        <form
        action="/api/v0/billing/create-checkout-session?mode=subscription"
        method="POST"
        >
        <input
        type="hidden"
        name="lookup_key"
        value={"simple_test_yearly"}
        />
        <input type="hidden" name="quantity" value="1" />
        <button
        id="checkout-and-portal-button-test"
        type="submit"
        className="w-100 btn btn-lg btn-success"
        style={{width: "50px", maxWidth: "100px", backgroundColor: "#dddddd", position: "absolute", right: "0px", border: "white 1px solid"}}
        >
        Test
        </button>
        </form>
      ) : (
        <button
        type="button"
        className="w-100 btn btn-lg btn-success"
        >
        <a className="btn-link" href="/signup">
        Sign up
        </a>
        </button>
      )}
      </div>
    </>
  );
};
