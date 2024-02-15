import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import { Link } from "react-router-dom";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import introDoc from "../docs/intro.md";

export const SidePanel = () => {
  const [content, setContent] = useState("");

  return (
    <div className="navbar-nav navbar-left justify-content-start col-sm-3 pe-3 p-3">
      {/*<div class="col-auto col-md-3 col-xl-2 px-sm-2 px-0">*/}
      <h3>Docs</h3>
      <Link to="/docs/getting-started" className="nav-link">
        Getting started
      </Link>
      <div className="nav-link">
        <a href="/openapi">API</a>
      </div>
    </div>
  );
};

const revealToken = (ev) => {
  //console.log(ev);
  const target = ev.target;
  const span = document.getElementById("token-output");
  if(span.innerHTML==""){
    span.innerHTML=localStorage.getItem("token");
    target.classList.remove("bi-envelope");
    target.classList.add("bi-envelope-open");
  }
  else {
    span.innerHTML="";
    target.classList.remove("bi-envelope-open");
    target.classList.add("bi-envelope");
  }
  ev.preventDefault( );
};

const getMyLoggedInToken = () => {
  const loggedIn = localStorage.getItem("loggedIn");
  if(!loggedIn){
    return (
      <></>
    );
  }
  else {
    return (

    <>
      <div id="get-jwt-token">
      <Link to="/" className="text-right" onClick={revealToken}>
      <span title="Click here to get your current JWT token..."
            className="get-jwt-token bi bi-envelope"></span>
      </Link>
      <br />
      <span id="token-output"></span>
      </div>
    </>
    );
  }
};

export const Docs = () => {
  const [content, setContent] = useState("");

  useEffect(() => {
    fetch(introDoc)
      .then((response) => response.text())
      .then((text) => {
        setContent(text);
      });
  });

  return (
    <>
      <div className="container-fluid">
        <div className="row flex-nowrap">
          <SidePanel />
          <div className="row">
            <div className="col-sm-9 p-5">
              {getMyLoggedInToken()}
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                children={content}
                components={{
                  code({ node, inline, className, children, ...props }) {
                    const match = /language-(\w+)/.exec(className || "");
                    return !inline && match ? (
                      <SyntaxHighlighter
                        children={String(children).replace(/\n$/, "")}
                        language={match[1]}
                        {...props}
                      />
                    ) : (
                      <code className={className} {...props}>
                        {children}
                      </code>
                    );
                  },
                }}
              />
            </div>
          </div>
        </div>
      </div>
    </>
  );
};
