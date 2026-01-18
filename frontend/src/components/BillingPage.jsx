import { useEffect, useState } from "react";
import { NoMatch } from "./NoMatch";

const SubscribeSuccess = ({ sessionId }) => {
  const sendSessionId = async () => {
    const response = await fetch("/api/v0/billing/subscribe", {
      method: "POST",
      headers: {
        "Content-type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
      body: JSON.stringify({ session_id: sessionId }),
    });

    if (!response.ok) {
      console.error(
        "Error: Stripe checkout has succeeded, but request to record this with Nyrkiö failed. " +
          response.status +
          " " +
          response.statusText,
      );
    }
  };

  useEffect(() => {
    sendSessionId();
  }, []);

  return (
    <>
    <div className="container text-center">
      <div className="row justify-content-center">
        <div className="col-md-8">
          <h1>You're subscribed!</h1>
          <p>Thank you! Your subscription has been processed successfully.</p>
        </div>
      </div>
    </div>
    <UserBillingPage />
    </>
  );
};

const SubscribeCancel = () => {
  return (
    <>
    <div className="container text-center">
      <div className="row justify-content-center">
        <div className="col-md-8">
          <h1>Checkout process was cancellled.</h1>
          <p>If you have questions or something isn't working, please contact sales@nyrkio.com.</p>
        </div>
      </div>
    </div>
    <UserBillingPage />
    </>
  );
};

const UserBillingPage = () => {
  const [billingPlan, setBillingPlan] = useState("free");
  const [runnerPlan, setRunnerPlan] = useState();
  const [meterStatus, setMeterStatus] = useState([]);
  const [loading, setLoading] = useState(true);
  const fetchBillingInfo = async () => {
    const response = await fetch("/api/v0/user/config", {
      headers: {
        "Content-type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    });

    if (!response.ok) {
      console.error(
        "Failed to fetch billing info: " +
          response.status +
          " " +
          response.statusText,
      );
      return;
    }

    const data = await response.json();
    console.debug(data);

    if (data.billing && data.billing.plan) {
      setBillingPlan(data.billing.plan);
    }
    if (data.billing_runners && data.billing_runners.plan) {
      setRunnerPlan(data.billing_runners.plan);

    }
    setLoading(false);
  };

  const getMeteredUsageStatus = async () => {
    const response = await fetch("/api/v0/user/meters", {
      headers: {
        "Content-type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    });
    if (!response.ok) {
      console.error(
        "Failed to fetch meter status (cpu-hours): " +
        response.status +
        " " +
        response.statusText,
      );
    }

    const data = await response.json();
    console.debug(data);
    setMeterStatus(data.data);
  };



  const SelectOrgs = () => {
    const username = localStorage.getItem("username");
    const [orgs, setOrgs] = useState(["-"]);

    const getOrganizations = async () => {
      const url = "/api/v0/orgs/";
      console.debug("GET " + url);
      const response = await fetch(url, {
        headers: {
          "Content-type": "application/json",
          Authorization: "Bearer " + localStorage.getItem("token"),
        },
      });

      if (response.status !== 200) {
        console.error("Failed to GET User's organizations");
        console.log(response);
        return response;
      } else console.debug(response);

      const data = await response.json();
      console.debug(data);
      if ( Array.isArray(data)  ) {
        return data;
      } else {
        return ["Fetching your organizations failed."];
      }
    };

    useEffect(() => {
      getOrganizations().then((data) => {
        console.log(data);
        if(data.forEach) {
        var temp = [];
        data.forEach((d) => {
          temp.push(d.organization.login);
        });

        setOrgs(
          temp.map((orgName) => {
            return (
            <>
            <input type="checkbox" name={orgName} checked={true} /> {orgName}  &nbsp; &nbsp;
            </>
            );
          })
        );
      }});
    }, []);


    return (
                <form action="/billing" className="card-body-text" >
                {orgs}
                </form>
    );
  };





  const CpuHoursTableData = ({stripedata}) => {
    const initialRows = 3;
    let rownr = 0;
    return stripedata.map(day =>
      <tr key={day.id} className={rownr++ >= initialRows? "stripedataCollapse" : ""}>
      <td>{new Date(day.start_time*1000).toDateString()}</td>
      <td style={{textAlign: "right"}}>{Math.round(1000*day.aggregated_value)/1000}</td>
      <td style={{textAlign: "left"}}>Cpu-Hours,</td>
      <td style={{textAlign: "right", width:"1em"}}> =</td>
      <td style={{textAlign: "right", width:"3em"}}>{Math.round(day.aggregated_value*10)/100} </td>
      <td style={{textAlign: "left", width:"3em"}}>€</td>
      </tr>
           );
  };

  let toggleVisibility = false;
  const collapseTable = (e) => {
    e.preventDefault();

    const t = document.getElementById("cpuhoursTable");
    if ( ! toggleVisibility ) {
      t.classList.add("stripedataShowAll");
    }
    else {
      t.classList.remove("stripedataShowAll");
    }
    toggleVisibility = !toggleVisibility;
  }

  const CpuHoursTable = ({stripedata}) => {
    let totalHours = 0;
    let totalEuros = 0;
    stripedata.map((day) => {
      totalHours = totalHours + day.aggregated_value;
      totalEuros = totalEuros + day.aggregated_value / 10;
    });
    return (<>
      <div className="cpuhours">
      <table id="cpuhoursTable" className="cpuhours stripedata">
      <thead>
      <tr>
         <th>Consumption past 30 days</th>
         <th style={{textAlign: "right"}}>{Math.round(1000*totalHours)/1000}</th>
         <th style={{textAlign: "left"}}>Cpu-Hours</th>
         <th style={{textAlign: "right"}}>=</th>
         <th style={{textAlign: "right"}}>{Math.round(totalEuros*100)/100}</th>
         <th style={{textAlign: "left"}}>€ *</th>
         </tr>
      </thead>
      <tbody>
      <CpuHoursTableData stripedata={stripedata} />
      <tr><td colSpan={6} style={{textAlign: "right"}}></td></tr>
      </tbody>
      <tfoot>
      <tr><th><a href="#" onClick={(e) => collapseTable(e)}><em>more<big>...</big></em></a></th>
          <th colSpan={5} style={{textAlign:"right"}}>*) prices without tax</th>
        </tr>
      </tfoot>
      </table>
      </div>
    </>)
  };

  useEffect(() => {
    setLoading(true);
    fetchBillingInfo();
    getMeteredUsageStatus();
  }, []);

  if (loading) {
    return <p>Loading...</p>;
  }

  const planMap = {
    free: "Free",
    simple_business_monthly: "Nyrkiö Business (Monthly)",
    simple_business_yearly: "Nyrkiö Business (Annual)",
    simple_enterprise_monthly: "Nyrkiö Enterprise (Monthly)",
    simple_enterprise_yearly: "Nyrkiö Enterprise (Annual)",
    simple_business_monthly_251: "Nyrkiö Business (Monthly)",
    simple_business_yearly_2409: "Nyrkiö Business (Annual)",
    simple_enterprise_monthly_627: "Nyrkiö Enterprise (Monthly)",
    simple_enterprise_yearly_6275: "Nyrkiö Enterprise (Annual)",
    simple_test_monthly: "Nyrkiö Test subscriptions (Monthly)",
    simple_test_yearly: "Nyrkiö Test subscriptions (Annual)",
    runner_postpaid_10: "Monthly CpuHours",
    runner_postpaid_13: "Monthly CpuHours",
    runner_prepaid_10: "Prepaid 100 CpuHours",
  };

  const onClick = async () => {
    const response = await fetch("/api/v0/billing/create-portal-session", {
      headers: {
        "Content-type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    });

    let portalSession = await response.json();
    console.debug(portalSession);
    if (!response.ok) {
      console.error(
        "Failed to create portal session: " +
          response.status +
          " " +
          response.statusText,
      );
      return;
    }
    window.location.href = portalSession.session.url;
  };

  const BillingButton = ({plan}) => {
    console.debug(`plan: {plan}`);


    if(plan=="Free" || plan === undefined) {
      return (
        <a className="btn btn-success" href="/pricing">
          Upgrade to Nyrkiö Business
        </a>

      );
    }else{
      return (
        <a className="btn btn-success" onClick={onClick}>
        Manage subscription (Stripe)
        </a>
      );
    }

  };

  return (
    <div className="container text-center">
      <div className="row justify-content-center">
        <div className="col-md-8">
          <h1>Billing</h1>
          <p>Manage your subscription here.</p>
        </div>
      </div>
      {runnerPlan?(
      <>
      <div className="row p-5">
        <div className="card nyrkio-billing">
          <div className="card-body shadow">
            <h3 className="card-title">Nyrkiö Runner for GitHub</h3>
            <p className="card-body-text">{planMap[runnerPlan]}</p>
            <p className="card-body-text">Orgs covered by this subscription:
            <SelectOrgs /></p>
            <CpuHoursTable stripedata={meterStatus} />
            <BillingButton plan={planMap[runnerPlan]}/>
          </div>
        </div>
      </div>
      </>
       ):""}
      {!runnerPlan || billingPlan != "free"?(
      <>
      <div className="row p-5">
        <div className="card nyrkio-billing">
          <div className="card-body shadow">
            <h3 className="card-title">Current plan</h3>
            <p className="card-body-text">{planMap[billingPlan]}</p>

            <BillingButton plan={planMap[billingPlan]}/>
          </div>
        </div>
      </div>
      </>
       ):""}
      <div className="row p-5">
      <p>Want to upgrade your subscription, or need professional services? Check out all Nyrkiö <a href="/pricing">products</a> and <a href="/services">services</a>.</p>
      </div>
    </div>
  );
};

export const BillingPage = ({ loggedIn }) => {
  const [subscribe_success, setSubscribeSuccess] = useState(false);
  const [subscribe_cancel, setSubscribeCancel] = useState(false);
  const [sessionId, setSessionId] = useState(null);

  useEffect(() => {
    const query = new URLSearchParams(window.location.search);

    if (query.get("subscribe_success")) {
      setSessionId(query.get("session_id"));
      setSubscribeSuccess(true);
    }

    if (query.get("subscribe_cancel")) {
      setSubscribeCancel(true);
    }
  }, []);

  // TODO(mfleming) We need a better way of doing this that doesn't require
  // every page to implement this logic. Maybe using AuthProvider?
  if (!loggedIn) {
    return <NoMatch />;
  }

  if (subscribe_success) {
    return <SubscribeSuccess sessionId={sessionId} />;
  }

  if (subscribe_cancel) {
    return <SubscribeCancel />;
  }

  return <UserBillingPage />;
};
