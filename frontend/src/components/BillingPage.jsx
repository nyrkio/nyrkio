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
        "Failed to send session ID: " +
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
  const [meterStatus, setMeterStatus] = useState();
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
      const meter = await getMeteredUsageStatus();
      setMeterStatus(meter);
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
      return;
    }

    const data = await response.json();
    console.debug(data);
    return data;
  };

  const CpuHoursTableData = ({stripedata}) => {
    for (let day of stripedata.data) {
      (<tr id={day.id} >
      <td>{new Date(day.start_time)}</td>
      <td>{day.aggregated_value}</td>
      <td>Cpu-Hours</td>
      <td>({day.aggregated_value*10} €)</td>
      </tr>)
    }

  }
  const CpuHoursTable = ({stripedata}) => {
    return (<>
      <table className="cpuhours stripedata">
      <CpuHoursTableData stripedata={stripedata} />
      </table>
    </>)
  };

  useEffect(() => {
    setLoading(true);
    fetchBillingInfo();
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
    simple_test_monthly: "Nyrkiö Test subscriptions (Monthly)",
    simple_test_yearly: "Nyrkiö Test subscriptions (Annual)",
    runner_postpaid_10: "Monthly CpuHours",
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
            <CpuHoursTable stripedata={runnerPlan} />

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
