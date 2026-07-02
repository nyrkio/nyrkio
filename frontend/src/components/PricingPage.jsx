import { useState } from "react";
import { DemoVideo } from "./FrontPage";
import { PricingCard } from "./PricingCard/PricingCard.jsx";
import { Icon } from "./Icon.jsx";

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

  const BusinessPricingCard = () => {
    const businessFinalPrice = annualDiscount
      ? (businessPrice * 12 * (1 - annualSavingsPercent / 100))
      : businessPrice;

    const businessPeriod = annualDiscount ? " eur/yr" : " eur/mo";

    return (
      <PricingCard
        className="h-100"
        title="Business"
        pricing={{
          price: businessFinalPrice,
          period: businessPeriod,
        }}
      >
        <PricingCard.FeatureList>
          <li>1 Git repository</li>
          <li>1600 cpu-hours / month</li>
          <li>Email and Slack notifications</li>
          <li>Support for teams</li>
        </PricingCard.FeatureList>

        <PricingCard.CTA>
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
              <input type="hidden"  name="quantity" value="1" />
              <input type="hidden" name="mode" value="subscription" />
              <button
                id="checkout-and-portal-button-business"
                type="submit"
                className="btn btn-primary w-100"
              >
                Subscribe
              </button>
            </form>
          ) : (
            <a className="btn btn-primary w-100" href="/signup">Sign up</a>
          )}
        </PricingCard.CTA>
      </PricingCard>
    );
  }

  const EnterprisePricingCard = () => {
    let enterpriseFinalPrice = "";
    let enterprisePeriod = "";
    let enterpriseTax = "+Tax";

    if (enterprisePrice === null) {
      enterpriseFinalPrice = "Call us";
      enterprisePeriod = "";
      enterpriseTax = "";
    } else if (annualDiscount) {
      enterpriseFinalPrice = (enterprisePrice * 12 * (1 - annualSavingsPercent / 100));
      enterprisePeriod = " eur/yr";
    } else {
      enterpriseFinalPrice = enterprisePrice;
      enterprisePeriod = " eur/mo";
    }

    return (
      <PricingCard
        className="h-100"
        title="Enterprise"
        pricing={{
          price: enterpriseFinalPrice,
          period: enterprisePeriod,
          tax: enterpriseTax
        }}
      >

        <PricingCard.FeatureList>
          <li>10 Git repositories</li>
          <li>4000 cpu-hours / month</li>
          <li>SSO (OneLogin, Okta)</li>
          <li>JIRA integration</li>
        </PricingCard.FeatureList>


        <PricingCard.CTA>
          {enterprisePrice === null ? (
            <a className="btn btn-lg btn-primary w-100 p-3" href="/contact">
              Contact Sales
            </a>
          ) : loggedIn ? (
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
                <input type="hidden"  name="quantity" value="1" />
                <input type="hidden" name="mode" value="subscription" />
                <button
                  id="checkout-and-portal-button-enterprise"
                  type="submit"
                  className="btn btn-primary w-100"
                >
                  Subscribe
                </button>
              </form>
            ) : (<a className="btn btn-primary w-100" href="/signup">Sign up</a>
            )}
        </PricingCard.CTA>
      </PricingCard>
    );
  }

  const FreePricingCard = () => {
    return (
      <PricingCard
        className="h-100"
        title="Free"
        pricing={{
          price: 0,
          period: 'eur/mo',
        }}
      >
        <PricingCard.FeatureList>
          <li>1 Git branch</li>
          <li>10 tests per branch</li>
          <li>10 metrics per test</li>
          <li>History of 100 points per metric</li>
        </PricingCard.FeatureList>
        <PricingCard.CTA>
          <a className="btn btn-primary w-100" href="/signup">Sign up for free</a>
        </PricingCard.CTA>
      </PricingCard>
    );
  }

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


  const pricingCardColClass = loggedIn ? 'col-lg-4 mb-5 mb-md-6' : 'col-md-6 col-lg-3 mb-5 mb-md-6';

  return (
    <>
      <div className="nyrkio-pricing container py-3">
        <h1 className="text-primary text-center">Pricing</h1>
        <div className="d-flex justify-content-center mt-5 mb-6" id="annual_discount_label">
          <div className="form-check form-switch d-flex d-md-block flex-column align-items-center text-center p-0">
            <input
              className="form-check-input mb-2 ms-0 mb-md-0 me-2"
              type="checkbox"
              role="switch"
              id="flexSwitchAnnual"
              onChange={updateDiscount}
            />
            <label className="form-check-label" htmlFor="flexSwitchAnnual">
              Save {bannualSavingsEuro} € or {annualSavingsEuro} € ({annualSavingsPercent} %) <br className="d-md-none" />by paying for the full year up front!
            </label>
          </div>
        </div>
        <div className="row">
          { !loggedIn ?
            (<div className={pricingCardColClass}><FreePricingCard /></div>) :
            ('')
          }

          <div className={pricingCardColClass}>
            <CpuHours loggedIn={loggedIn}/>
          </div>
          <div className={pricingCardColClass}>
            <BusinessPricingCard />
          </div>

          <div className={pricingCardColClass}>
            <EnterprisePricingCard />
          </div>
        </div>

        <DemoVideo />

        <h3 className="text-center text-secondary mb-4">Compare plans</h3>
        <div className="table-responsive rounded shadow">
          <table className="table-price table table-bordered text-center border-light align-middle">
            <thead>
            <tr>
              <th style={{ width: "200px" }}>Name</th>
              <th style={{ width: "20%" }}>Free</th>
              <th style={{ width: "20%" }}>Runner</th>
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
              <td>10</td>
            </tr>
            <tr>
              <th scope="row" className="text-start">
                CPU-Hours / month
              </th>
              <td>1</td>
              <td>10</td>
              <td>Unlimited</td>
              <td> - </td>
            </tr>
            <tr>
              <th scope="row" className="text-start">
                GitHub PR gating
              </th>
              <td>
                <div className="d-flex justify-content-center">
                  <Icon name="check-mark-circle" size="24" />
                </div>
              </td>
              <td>
                <div className="d-flex justify-content-center">
                  <Icon name="check-mark-circle" size="24" />
                </div>
              </td>
              <td>
                <div className="d-flex justify-content-center">
                  <Icon name="check-mark-circle" size="24" />
                </div>
              </td>
              <td>
                <div className="d-flex justify-content-center">
                  <Icon name="check-mark-circle" size="24" />
                </div>
              </td>
            </tr>
            <tr>
              <th scope="row" className="text-start">
                GitHub organization support
              </th>
              <td> - </td>
              <td>
                <div className="d-flex justify-content-center">
                  <Icon name="check-mark-circle" size="24" />
                </div>
              </td>
              <td>
                <div className="d-flex justify-content-center">
                  <Icon name="check-mark-circle" size="24" />
                </div>
              </td>
              <td>
                -
              </td>
            </tr>
            <tr>
              <th scope="row" className="text-start">
                Slack alerts
              </th>
              <td> - </td>
              <td>
                <div className="d-flex justify-content-center">
                  <Icon name="check-mark-circle" size="24" />
                </div>
              </td>
              <td>
                <div className="d-flex justify-content-center">
                  <Icon name="check-mark-circle" size="24" />
                </div>
              </td>
              <td>
                <div className="d-flex justify-content-center">
                  <Icon name="check-mark-circle" size="24" />
                </div>
              </td>
            </tr>
            <tr>
              <th scope="row" className="text-start">
                Jira integration
              </th>
              <td>-</td>
              <td>-</td>
              <td>-</td>
              <td>
                <div className="d-flex justify-content-center">
                  <Icon name="check-mark-circle" size="24" />
                </div>
              </td>
            </tr>
            <tr>
              <th scope="row" className="text-start">
                Security
              </th>
              <td>-</td>
              <td>-</td>
              <td>-</td>
              <td>Dedicated VPC, peering, or run on your own infrastructure</td>
            </tr>
            <tr>
              <th scope="row" className="text-start">
                Single sign-on (OneLogin, Okta)
              </th>
              <td>-</td>
              <td>-</td>
              <td>-</td>
              <td>
                <div className="d-flex justify-content-center">
                  <Icon name="check-mark-circle" size="24" />
                </div>
              </td>
            </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div className="container text-center mt-4 mt-md-6">
        {loggedIn ? (
          <form action="/api/v0/billing/create-checkout-session?mode=subscription"
                method="POST">
            <input
              type="hidden"
              name="lookup_key"
              value={"simple_test_yearly"}/>
            <input type="hidden"  name="quantity" value="1" />
            <input type="hidden" name="mode" value="subscription" />
            <button
              id="checkout-and-portal-button-test"
              type="submit"
              className="btn btn-primary w-100 w-md-auto">Get Started</button>
          </form>
        ) : (<a className="btn btn-primary w-100 w-md-auto" href="/signup">Sign up</a>)}
      </div>
    </>
  );
};

const prePaidToBeUsedLater = () => {
  return ( <>
            <div className="col">
            <div className="card mb-4 rounded-3 shadow-sm border-success m-4">
              <div className="card-header py-3">
                <h4 className="my-0 fw-normal">Nyrkiö Runner</h4>
                <span className="text-shoulders">Pre-paid</span>
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

export const CpuHours = ({loggedIn, short}) => {
  return (
    <>
      <PricingCard
        className="h-100"
        title="Nyrkiö Runner"
        subtitle="For GitHub"
        short={short}
        pricing={{
          price: "0.1",
          period: "eur/hour/cpu",
        }}
      >
        <PricingCard.FeatureList>
          <li>Pay as you go, monthly</li>
          <li>High Fidelity c7a instances</li>
          <li>Tuned for <em>stable performance</em></li>
          <li>Change Detection & Graphs included</li>
        </PricingCard.FeatureList>

        <PricingCard.CTA>
          {loggedIn ? (<form
            action="/api/v0/billing/create-checkout-session-postpaid?mode=subscription"
            method="POST"
          >
            <input
              type="hidden"
              name="lookup_key"
              value="runner_postpaid_13"
            />
            <input type="hidden"  name="mode" value="subscription"/>
            <button
              id="checkout-and-portal-button-runner_postpaid_10"
              type="submit"
              className="btn btn-primary w-100"
            >
              Subscribe (pay after use)
            </button>
          </form>) : (<a className="btn btn-primary w-100" href="/signup">Log in &amp; Subscribe</a>)}
        </PricingCard.CTA>
      </PricingCard>
    </>
  );
}
