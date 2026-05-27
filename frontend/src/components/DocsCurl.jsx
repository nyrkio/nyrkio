import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import introDoc from "../docs/intro.md";
import img1 from "../static/getting-started-login-button.png";
import img2 from "../static/getting-started-login.png";
import img3 from "../static/getting-started-UserSettings.png";
import img4 from "../static/getting-started-API-key.png";

export const DocsCurl = () => {
  const [content, setContent] = useState("");

  useEffect(() => {
    fetch(introDoc)
      .then((response) => response.text())
      .then((text) => {
        setContent(text);
      });
  }, []);

  return (
    <>
      <div className="container text-center nyrkio-docs">
        <h1 className="text-primary mb-4 mb-md-5">Using the Nyrkio HTTP API</h1>
        <p className="mb-0">
          For CI systems other than GitHub Actions, or for custom integrations,
          you can use the Nyrkio REST API directly. This tutorial shows how to
          upload benchmark results using <code className="badge text-bg-secondary">curl</code>.
        </p>
        <p className="mb-4">
          For GitHub users, see the Getting started guide for the
          easier approach using Nyrkio Runners and the change-detection action.
        </p>

        <a className="btn btn-primary w-100 w-md-auto" href="/docs/getting-started">Getting started guide</a>
        <FirstHalfCurl />
        <div className="markdown-container">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            children={content}
            components={{
              h2: ({node, ...props}) => <h2 className="h3 text-secondary text-center mt-4 mt-md-5 mb-4" {...props} />,
              h3: ({node, ...props}) => <h3 className="h3 text-secondary text-center mt-4 mt-md-5 mb-4" {...props} />,
              ul: ({node, ...props}) => <ul className="d-inline-block text-start" {...props} />,
              table: ({node, ...props}) => <div className="table-responsive rounded shadow mb-3"><table className="table table-bordered text-center border-light align-middle" {...props} /></div>,
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
        <hr className="my-4 my-md-6"/>
      </div>
    </>
  );
};

const FirstHalfCurl = () => {
  return (
    <>
      <div className="mt-section">
        <h2 className="h3 text-secondary mb-3 mb-md-4" id="getting-started-curl">1. Create a user account</h2>

        <div className="row">
          <div className="col-md-6">
            <p>Click on the Login button in the top right corner:</p>
            <img width="179" height="109" loading="lazy" src={img1} alt="Login button" className="img-fluid border border-2 border-secondary rounded shadow"/>
          </div>
          <div className="col-md-6">
            <p>Choose between GitHub OAuth or traditional username + password logins.</p>
            <img width="600" height="538" loading="lazy" src={img2} alt="Login options" className="img-fluid border border-2 border-secondary rounded shadow"/>
          </div>
        </div>
      </div>

      <hr className="my-4 my-md-6" />

      <div className="mb-section">
        <h2 className="h3 text-secondary mb-3 mb-md-4">2. Create a JWT token</h2>
        <div className="row">
          <div className="col-md-4">
            <p>
              We use JWT to access the Nyrkio API. Click on the user menu (top
              right) and select <strong>User Settings</strong>.
            </p>
            <img src={img3} width="219" height="244" loading="lazy" alt="User settings menu" className="img-fluid border border-2 border-secondary rounded shadow"/>
          </div>
          <div className="col-md-8">
            <p>Create a new API key and save it somewhere secure.</p>
            <img src={img4} width="907" height="179" loading="lazy" alt="API key creation" className="img-fluid border border-2 border-secondary rounded shadow"/>
          </div>
        </div>
      </div>
    </>
  );
};
