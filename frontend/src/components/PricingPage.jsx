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
        style={{ maxWidth: "2000px" }}
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
                  className="w-100 btn btn-lg btn-outline-success p-3"
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
                  <small><span style={{color:"#555555", fontFamily:"Helvetica, Arial, Inter, sans", fontSize:"50%", letterSpacing:"0.0"}}>+Tax</span></small>
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
                    action={`/api/v0/billing/create-checkout-session?mode=subscription&lookup_key=${annualDiscount ? "simple_business_yearly" : "simple_business_monthly"}&quantity=1`}
                    method="POST"
                  >
                    <input
                      type="hidden"
                      name="lookup_key"
                      value={
                        annualDiscount ? "simple_business_yearly_2409" : "simple_business_monthly_251"
                      }
                    />
                    <input type="hidden" name="access_token" value={localStorage.getItem("token")} />
                    <input type="hidden" name="quantity" value="1" />
                    <input type="hidden" name="mode" value="subscription" />
                    <button
                      id="checkout-and-portal-button-business"
                      type="submit"
                      className="w-100 btn btn-lg btn-success p-3"
                    >
                      Subscribe
                    </button>
                  </form>
                ) : (
                  <button
                    type="button"
                    className="w-100 btn btn-lg btn-success p-3"
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
                  <small><span style={{color:"#555555", fontFamily:"Helvetica, Arial, Inter, sans", fontSize:"50%", letterSpacing:"0.0"}}>+Tax</span></small>
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
                          ? "simple_enterprise_yearly_6275"
                          : "simple_enterprise_monthly_627"
                      }
                    />
                    <input type="hidden" name="access_token" value={localStorage.getItem("token")} />
                    <input type="hidden" name="quantity" value="1" />
                    <input type="hidden" name="mode" value="subscription" />
                    <button
                      id="checkout-and-portal-button-enterprise"
                      type="submit"
                      className="w-100 btn btn-lg btn-success p-3"
                    >
                      Subscribe
                    </button>
                  </form>
                ) : (
                  <button
                    type="button"
                    className="w-100 btn btn-lg btn-success p-3"
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
      <div style={{opacity: 0.01, width: "100px", position: "absolute", right: "0px"}} >
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
        <input type="hidden" name="access_token" value={localStorage.getItem("token")} />
        <input type="hidden" name="quantity" value="1" />
        <input type="hidden" name="mode" value="subscription" />
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
        className="w-100 btn btn-lg btn-success p-3"
        >
        <a className="btn-link" href="/signup">
        Sign up
        </a>
        </button>
      )}
      </div>

      {loggedIn ? (<>
        <hr />

      <div
        className="nyrkio-pricing container py-3"
      >
        <div className="container-fluid justify-content-center text-center w-100">
          <h2>Closed beta for logged in users only...</h2>
        </div>

        <p>This is for testing only, exact content of each product is still TBD</p>
        <p>Run your continuous benchmarking on c7a family instances, configured by Nyrkiö for maximal stable and repeatable performance. Pricing is per hour per CPU.</p>

        <div className="nyrkio-plans row row-cols-1 row-cols-lg-3 text-center justify-content-center">

          <div className="col">
            <div className="card mb-4 rounded-3 shadow-sm border-success m-4">
              <div className="card-header py-3">
                <h4 className="my-0 fw-normal">Nyrkiö Runner</h4>
                <span className="text-shoulders">for GitHub</span>
              </div>
              <div className="card-body">
                <h1 className="card-title pricing-card-title">
                  <span style={{letterSpacing: "4px"}}>0</span><span style={{letterSpacing: "-3px"}}>.1</span><span style={{letterSpacing: "12px"}}> </span><small className="text-body-secondary fw-light" style={{letterSpacing: "2px"}}> eur/hour/cpu
                  <span style={{color:"#555555", fontFamily:"Helvetica, Arial, Inter, sans", fontSize:"50%", letterSpacing:"0.0"}}>+Tax</span></small>
                </h1>
                <ul className="list-unstyled mt-3 mb-4">
                  <li>Pay as you go, monthly</li>
                  <li>High Fidelity c7a instances</li>
                  <li>Tuned for <em>stable performance</em></li>
                  <li>Change Detection & Graphs included</li>
                </ul>
                  <form
                    action="/api/v0/billing/create-checkout-session-postpaid?mode=subscription"
                    method="POST"
                  >
                    <input
                      type="hidden"
                      name="lookup_key"
                      value="runner_postpaid_13"
                    />
                    <input type="hidden" name="access_token" value={localStorage.getItem("token")} />
                    <input type="hidden" name="mode" value="subscription" />
                    <button
                      id="checkout-and-portal-button-runner_postpaid_10"
                      type="submit"
                      className="w-100 btn btn-lg btn-success p-3"
                    >
                      Subscribe (pay after use)
                    </button>
                  </form>
              </div>
            </div>
          </div>
          </div>
          </div>
          </>):
          ""}
    </>
  );
};

const prePaidToBeUsedLater = () => {
  return ( <>

            <div className="col">
            <div className="card mb-4 rounded-3 shadow-sm border-success m-4">
              <div className="card-header py-3">
                <h4 className="my-0 fw-normal">Nyrkiö Runner</h4>
                <span class="text-shoulders">Pre-paid</span>
              </div>
              <div className="card-body">
                <p className="nyrkio-annual"></p>
                <h1 className="card-title pricing-card-title">
                  9 <small className="text-body-secondary fw-light"> eur</small>
                </h1>
                <ul className="list-unstyled mt-3 mb-4">
                  <li></li>
                  <li>100 cpu-hours</li>
                  <li>10% discount when pre-paying</li>
                </ul>
                  <form
                    action="/api/v0/billing/create-checkout-session-prepaid?mode=payment"
                    method="POST"
                  >
                    <input
                      type="hidden"
                      name="lookup_key"
                      value="runner_prepaid_100"
                    />
                    <input type="hidden" name="access_token" value={localStorage.getItem("token")} />
                    <select id="runner_prepaid_100_quantity" name="quantity" defaultValue={1} style={{width: "90%"}}>
                      <option value="100">1 pack, 100 cpu-hours</option>
                      <option value="200">2 pack, 200 cpu-hours</option>
                      <option value="300">3 pack, 300 cpu-hours</option>
                      <option value="400">4 pack, 400 cpu-hours</option>
                      <option value="500">5 pack, 500 cpu-hours</option>
                      <option value="1000">10 pack, 1000 cpu-hours</option>
                      <option value="-1">For larger quantities, please buy suitable subscription above</option>
                    </select>
                    <button
                      id="checkout-and-portal-button-runner_prepaid_100"
                      type="submit"
                      className="w-100 btn btn-lg btn-success p-3"
                    >
                      Checkout
                    </button>
                  </form>
              </div>
            </div>
          </div>
          </>
  );

};
