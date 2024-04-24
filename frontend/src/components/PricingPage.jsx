import { useEffect, useState } from "react";

export const PricingPage = ({ loggedIn }) => {
  const businessPriceFloor = 10;
  const businessPricePerHead = 20;
  const enterprisePriceFloor = 40;
  const enterprisePricePerHead = 40;
  const [businessPrice, setBusinessPrice] = useState(
    businessPriceFloor * businessPricePerHead
  );
  const [enterprisePrice, setEnterprisePrice] = useState(
    enterprisePriceFloor * enterprisePricePerHead
  );
  const cut1 = 100;
  const [annualDiscount, setAnnualDiscount] = useState(false);
  const [annualSavingsPercent, setAnnualSavingsPercent] = useState(20);
  const [annualSavingsEuro, setAnnualSavingsEuro] = useState(
    enterprisePrice * 12 * (annualSavingsPercent / 100)
  );
  const [busYear, setBusYear] = useState(businessPrice * 12);
  const [entYear, setEntYear] = useState(enterprisePrice * 12);
  const [eng, setEng] = useState(0);
  const [total, setTotal] = useState(0);

  const getBusPrice = (total) => {
    var b;
    if (total < cut1) {
      b = Math.max(
        businessPriceFloor * businessPricePerHead,
        total * businessPricePerHead
      );
      b = Math.round(b);
    } else if (total <= 5000) {
      b = (cut1 + 0.1 * (total - cut1)) * businessPricePerHead;
      b = Math.round(b);
    } else {
      b = null;
    }
    return b;
  };
  const getEntPrice = (total) => {
    var e;

    if (total < cut1) {
      e = Math.max(
        enterprisePriceFloor * enterprisePricePerHead,
        total * enterprisePricePerHead
      );
      e = Math.round(e);
    } else if (total <= 5000) {
      e = (cut1 + 0.15 * (total - cut1)) * enterprisePricePerHead;
      e = Math.round(e);
    } else {
      e = null;
    }
    return e;
  };

  /*
   * CPUH = CPU-Hours on a C7g instance type.
   *
   * Currently in Stockholm region $0.0387 / vcpu / hour and scales linearly with nr of cpu.
   * Since we'll turn off hyper threading (or avoid half the cpu's), we pay double, so use $0.0774/h.
   * In practice then a simple benchmark will run on a c7g.xlarge. (4 vcpu) and consume
   * two CPUH=0.0774 per hour. Benchmarks requiring a larger server or even a cluster will simply pay more per hour.
   * CPUH units will also be converted and consumed to cover EBS, network and other costs.
   *
   * TODO: verify whether dedicated or i.metal servers are needed. Hypothesis is no.
   */
  const CPUHdollars = 0.1 * 1.25; // round up from 0.0774 + 25% markup
  const dollarToEuro = 1; // Currently 0.93, round up to cover currency risk

  const getBusHours = (totalPrice) => {
    var exactly = (dollarToEuro * totalPrice) / 10 / CPUHdollars; // Allocate 10% of subscription for CPUH credits. Heavy users will have to pay more.
    var rounded = parseFloat(exactly.toPrecision(2)); // Note: With all the rounding going on ends up being more like 5%
    return rounded;
  };

  const getEntHours = (totalPrice) => {
    var exactly = (dollarToEuro * totalPrice) / 10 / CPUHdollars;
    var rounded = parseFloat(exactly.toPrecision(1));
    return rounded;
  };
  const [busHours, setBusHours] = useState(
    getBusHours(businessPriceFloor * businessPricePerHead)
  );
  const [entHours, setEntHours] = useState(
    getEntHours(enterprisePriceFloor * enterprisePricePerHead)
  );

  const updateDiscount = () => {
    const widget = document.getElementById("flexSwitchAnnual");
    if (widget) {
      setAnnualDiscount(widget.checked);
    }
  };

  const priceCalculator = (sourceElement) => {
    const localTotal = document.getElementById("employees_total").value;
    setTotal(document.getElementById("employees_total").value);
    setEng(document.getElementById("employees_engineering").value);
    var b = getBusPrice(localTotal);
    var e = getEntPrice(localTotal);

    setBusinessPrice(b);
    setEnterprisePrice(e);
    setBusYear(b * 12);
    setEntYear(e * 12);

    setBusHours(getBusHours(b));
    setEntHours(getEntHours(e));
    if (e) {
      setAnnualSavingsEuro(e * 12 * (annualSavingsPercent / 100));
    } else {
      setAnnualSavingsEuro(null);
    }
    return true;
  };

  const BusinessPrice = () => {
    if (businessPrice === null) {
      return <>Call us</>;
    }
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

  const AnnualSavingsEuro = () => {
    if (annualSavingsEuro === null) {
      return "";
    } else {
      return (
        <>
          That's {annualSavingsEuro} € for you! (For Enterprise subscription).
        </>
      );
    }
  };

  const NoticeEngineeringSmall = () => {
    //console.debug("If Engineering dept isn't 25-50% of total employees, give custom price after talking to them.")
    if (eng > 0 && total > 0 && eng / total < 0.25 && total < 1000) {
      console.debug("Small engineering dept -> custom price notice");
      return (
        <>
          <div className="nyrkio-pricing-note nyrkio-pricing-engineering-small">
            <p>
              Note: Our list price may not be perfect for your organization.
              Please <a href="mailto:sales@nyrkio.com">contact us</a> so we can
              discuss a more suitable pricing level. We want to ensure Nyrkiö is
              a good fit for projects large and small.
            </p>
          </div>
        </>
      );
    } else {
      return <></>;
    }
  };

  const NoticeTotalLarge = () => {
    //console.debug("If Engineering dept isn't 25-50% of total employees, give custom price after talking to them.")
    if (total > 999) {
      console.debug("Large total -> custom price notice");
      return (
        <>
          <div className="nyrkio-pricing-note nyrkio-pricing-engineering-small">
            <p>
              Note: Our list price may not be perfect for your organization.
              Please <a href="mailto:sales@nyrkio.com">contact us</a> so we can
              discuss a more suitable pricing level. We want to ensure Nyrkiö is
              a good fit for projects large and small.
            </p>
          </div>
        </>
      );
    } else {
      return <></>;
    }
  };

  /*
  const generatePricingTable = () => {
    var pricingTable = [];
    for (var zeros = 0; zeros <= 4; zeros++) {
      for (var i = 1; i < 10; i++) {
        var employees = i * Math.pow(10, zeros);
        //pricingTable.push(<ObjectRow key={employees} data={obj} />);
        pricingTable.push(
          <tr key={employees}>
            <td>{employees}</td>
            <td>
              {getBusPrice(employees)} / {getBusPrice(employees) * 12}
            </td>
            <td>
              {getEntPrice(employees)} / {getEntPrice(employees) * 12}
            </td>
            <td>
              {getBusHours(getBusPrice(employees))} /{" "}
              {(getBusHours(getBusPrice(employees)) / 2) *
                CPUHdollars *
                dollarToEuro}
              €
            </td>
            <td>
              {getEntHours(getEntPrice(employees))} /{" "}
              {(getEntHours(getEntPrice(employees)) / 2) *
                CPUHdollars *
                dollarToEuro}
              €
            </td>
          </tr>
        );
      }
    }
    return (
      <>
        <thead>
          <tr>
            <th>Employees</th>
            <th>Business €/mo &amp; yr</th>
            <th>Enterprise €/mo &amp; yr</th>
            <th>Business CPUH /mo &amp; $/mo</th>
            <th>Enterprise CPUH/mo &amp; $/mo</th>
          </tr>
        </thead>
        <tbody>{pricingTable}</tbody>
      </>
    );
  };
  */
  //const pricingTableRows = generatePricingTable();

  return (
    <>
      <div
        className="nyrkio-pricing container py-3"
        style={{ maxWidth: "960px" }}
      >
        <div className="row justify-content-center">
          <div className="text-center">
            <h1>Pricing</h1>
            <div className="p-3 mb-3">
              Pricing plans are simple: For small to medium sized companies,
              pricing is based on the size of your team or organization size.
              The subscription automatically covers all engineers, because we
              want to empower everyone on the team to be responsible for
              performance of their own code.
            </div>
          </div>
        </div>

        <div className="text-right rounded-3">
          <div className="p-3 calculator rounded-3 shadow-sm">
            <div className="row mb-3">
              <div className="col col-md-6" id="company_name_label">
                Company name:
              </div>
              <div className="col col-md-6">
                <input
                  type="text"
                  id="company_name"
                  name="company_name"
                  className="form-control"
                  onChange={priceCalculator}
                />
              </div>
            </div>
            <div className="row mb-3">
              <div className="col col-md-6" id="employees_total_label">
                Employees in the company:
              </div>
              <div className="col col-md-6">
                <input
                  type="text"
                  id="employees_total"
                  name="employees_total"
                  className="form-control"
                  onChange={priceCalculator}
                />
              </div>
            </div>
            <div className="row mb-3">
              <div className="col col-md-6" id="employees_engineering_label">
                Employees in Engineering/IT department:
              </div>
              <div className="col col-md-6">
                <input
                  type="text"
                  id="employees_engineering"
                  name="employees_engineering"
                  className="form-control"
                  onChange={priceCalculator}
                />
              </div>
            </div>
          </div>
        </div>

        <NoticeTotalLarge />
        <NoticeEngineeringSmall />

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
                  <li>10,000 test results</li>
                  <li>100 metrics per test</li>
                  <li>Email and Slack notifications</li>
                  <li>Support for teams</li>
                  <li>{busHours} cpu-hours/month*</li>
                </ul>
                {loggedIn ? (
                  <form
                    action="/api/v0/billing/create-checkout-session"
                    method="POST"
                  >
                    <input
                      type="hidden"
                      name="lookup_key"
                      value={
                        annualDiscount ? "business_yearly" : "business_monthly"
                      }
                    />
                    <input type="hidden" name="quantity" value={total} />
                    <button
                      id="checkout-and-portal-button"
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
                  <li>Everything in Business, plus...</li>
                  <li>Unlimited results and metrics</li>
                  <li>JIRA integration</li>
                  <li>24/7 support</li>
                  <li>{entHours} cpu-hours/month*</li>
                </ul>
                {loggedIn ? (
                  <form
                    action="/api/v0/billing/create-checkout-session"
                    method="POST"
                  >
                    <input
                      type="hidden"
                      name="lookup_key"
                      value={
                        annualDiscount
                          ? "enterprise_yearly"
                          : "enterprise_monthly"
                      }
                    />
                    <input type="hidden" name="quantity" value={total} />
                    <button
                      id="checkout-and-portal-button"
                      type="submit"
                      onClick={(e) => {
                        if (total <= 0) {
                          alert(
                            "Please enter number of employees in the company."
                          );
                          e.preventDefault();
                          return false;
                        }
                      }}
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
                  Save {annualSavingsPercent} % by paying for the full year up
                  front! <AnnualSavingsEuro />
                </label>
              </div>
            </div>
          </div>
        </div>

        <p>
          *){" "}
          <small>
            Coming soon: Benchmarking as a Service. We run your benchmarks on
            servers tuned to minimize random noise in the results.
          </small>
        </p>

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
                    <svg className="bi" width="24" height="24">
                      <use xlinkHref="#check" />
                    </svg>
                  </td>
                  <td>
                    <i className="bi bi-check"></i>
                  </td>
                </tr>
              </tbody>

              <tbody>
                <tr>
                  <th scope="row" className="text-start">
                    Integrations
                  </th>
                  <td></td>
                  <td>
                    Email
                    <br />
                    Slack
                  </td>
                  <td>
                    Email
                    <br />
                    Slack
                    <br />
                    JIRA
                  </td>
                </tr>
              </tbody>

              <tbody>
                <tr>
                  <th scope="row" className="text-start">
                    Benchmarking as a Service*
                  </th>
                  <td></td>
                  <td>{busHours} cpu-hours/month</td>
                  <td>{entHours} cpu-hours/month</td>
                </tr>
                <tr>
                  <th scope="row" className="text-start"></th>
                  <td colSpan="3" className="nyrkio-right">
                    <small>
                      Additional CPUH credits at {CPUHdollars * dollarToEuro}{" "}
                      EUR.
                    </small>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div className="row nyrkio-open-source">
          <div className="text-center">
            <h4>Open Source projects apply here...</h4>
            <div className="p-3 mb-3">
              We have a limited capacity, but whenever possible, we offer free
              Business subscriptions to Open Source projects. If you're
              interested, <a href="mailto:helloworld@nyrkio.com">email us!</a>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

/*
        <hr/>
        <div className="row nyrkio-pricing-table">
          <div className="text-center">
            <h3>Debug: pricing and infra costs for different company sizes</h3>
            <table>
            {pricingTableRows}
            </table>
          </div>
        </div>
*/
