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
    <div className="container text-center">
      <div className="row justify-content-center">
        <div className="col-md-8">
          <h1>You're subscribed!</h1>
          <p>Thank you! Your subscription has been processed successfully.</p>
        </div>
      </div>
    </div>
  );
};

const SubscribeCancel = () => {
  return (
    <div className="container text-center">
      <div className="row justify-content-center">
        <div className="col-md-8">
          <h1>Subscription cancelled</h1>
          <p>Oh no! Your subscription has been cancelled.</p>
        </div>
      </div>
    </div>
  );
};

const UserBillingPage = () => {
  const [billingPlan, setBillingPlan] = useState("free");
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
    setLoading(false);
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
    business_monthly: "Business (monthly)",
    business_yearly: "Business (Annual)",
  };

  const onClick = async () => {
    const response = await fetch("/api/v0/billing/create-portal-session", {
      headers: {
        "Content-type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    });

    if (!response.ok) {
      console.error(
        "Failed to create portal session: " +
          response.status +
          " " +
          response.statusText,
      );
      return;
    }
    window.location.href = response.url;
  };

  const BillingButton = ({plan}) => {
    if(plan="free") {
      return (
        <a className="btn btn-success" href="/pricing">
          Upgrade to Nyrkiö Business
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
      <div className="row p-5">
        <div className="card nyrkio-billing">
          <div className="card-body shadow">
            <h5 className="card-title">Current plan</h5>
            <p className="card-text">{planMap[billingPlan]}</p>
            <BillingButton plan={planMap[billingPlan]}/>
          </div>
        </div>
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
