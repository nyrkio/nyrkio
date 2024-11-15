import { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";

import Button from 'react-bootstrap/Button';


export const ImpersonateControls = () => {
  const [whoami , setWhoami] = useState({});

  useEffect(() => {
    getImpersonateUser().then((impersonate_user) => {
      setWhoami( impersonate_user || {});
    });
  }, []);


  const ActualImpersonateControls = ({whoami}) => {
    const stopIt = () => {
        stopImpersonateUser().then( (original_user) => {
            setWhoami(original_user);
            window.location.reload(true);
        });
    };

  if (whoami && "superuser" in whoami && "user_email" in whoami) {
    let admin_user = whoami.superuser.user_email;
    let titlemsg = "You are an administrator that has assumed the role of another user. Click here to return to your normal user account: " + admin_user;
  return (
    <>
    <Button href="/admin" className="btn btn-danger" onClick={(event) => { event.preventDefault(); stopIt();}}
    title={titlemsg}
    >  &#x2716; </Button>
    </>

  );
   }
   else {
     return "";
   }
  };

  return <ActualImpersonateControls whoami={whoami} />;
};


export const impersonateUser = async (impersonate_user) => {
  const fetchData = async () => {
    const body = {
          username: impersonate_user['email'],
          id: impersonate_user['_id'],
    };
    const results = await fetch("/api/v0/admin/impersonate", {
      method: "POST",
      headers: {
        "Content-type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
      body: JSON.stringify(body),
    });
    const resultData = await results.json();
    console.debug(resultData);
    if("superuser" in resultData){
      localStorage.setItem("username", resultData['user_email']);
      document.body.classList.add( "impersonate-user" );
    }

    return resultData;
  };
  return await fetchData();

};

const getImpersonateUser = async () => {
  const fetchData = async () => {
    const results = await fetch("/api/v0/admin/impersonate", {
      method: "GET",
      headers: {
        "Content-type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    });
    const resultData = await results.json();
    console.debug(resultData);
    if(resultData && 'user_email' in resultData) {
      localStorage.setItem("username", resultData['user_email']);
    }
    if(resultData && 'superuser' in resultData) {
      document.body.classList.add( "impersonate-user" );
    }
    else {
      document.body.classList.remove( "impersonate-user" );
    }
    return resultData;
  };
  return await fetchData();

};

const stopImpersonateUser = async () => {
  console.log("stopping");
  const fetchData = async () => {
    console.log("stopping fetchdata");
    const results = await fetch("/api/v0/admin/impersonate", {
      method: "DELETE",
      headers: {
        "Content-type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    });
    const resultData = await results.json();
    console.debug(resultData);
    localStorage.setItem("username", localStorage.getItem("username_real"))
    document.body.classList.remove( "impersonate-user" );
    return resultData;
  };
  return await fetchData();

};
