import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import { Link } from "react-router-dom";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import introDocAction from "../docs/intro-action.md";
import img3 from "../static/getting-started-UserSettings.png";
import img4 from "../static/getting-started-API-key.png";

export const DocsChangeDetection = () => {
  const [contentAction, setContentAction] = useState("");

  useEffect(() => {
    fetch(introDocAction)
      .then((response) => response.text())
      .then((text) => {
        setContentAction(text);
      });
  }, []);

  const MarkdownRenderer = ({ content }) => (
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
  );

  return (
    <>
      <div className="container nyrkio-docs">
        <Intro />
        <TokenSetup />
        <hr className="my-4 my-md-6"/>
        <div className="markdown-container text-center">
          <h2 className="h3 text-secondary mb-4">2. Add the GitHub Action</h2>
          <MarkdownRenderer content={contentAction} />
        </div>
        <hr className="my-4 my-md-6"/>
        <Credits />
      </div>
    </>
  );
};

const Intro = () => {
  return (
    <div className="text-center">
      <h1 className="text-primary text-center mb-4 mb-md-5">Change Point Detection</h1>
      <p className="mb-4">
        Nyrkio Change Detection automatically finds performance regressions and improvements in your benchmark history. When a change is detected, Nyrkio can notify you via a GitHub issue or Slack message.<br/>
        The easiest way to use Change Detection is the <a href="https://github.com/marketplace/actions/nyrkio-change-detection"><code>nyrkio/change-detection@v2</code></a> GitHub Action. It parses output from common benchmark frameworks and uploads results to nyrkio.com for analysis.<br/>
        For non-GitHub CI systems, see HTTP API documentation.
      </p>

      <a href="/docs/getting-started-http" className="btn btn-primary w-100 w-md-auto mb-section">HTTP API documentation</a>

      <h2 className="h3 text-secondary text-center">1. Create a JWT token</h2>
    </div>
  );
};

const TokenSetup = () => {
  return (
    <div className="text-center">
      <p>
        To upload results to the Nyrkio API, you need a JWT token. Click on the
        user menu (top right) and select <strong>User Settings</strong>.
      </p>

      <div className="row">
        <div className="col-md-4">
          <img src={img3} width="219" height="244" loading="lazy" alt="User settings menu" className="img-fluid border border-2 border-secondary rounded shadow"/>
          <p className="mt-2 mb-4 mb-md-0">Create a new API key and save it somewhere secure.</p>
        </div>
        <div className="col-md-8">
          <img src={img4} width="907" height="179" loading="lazy" alt="API key creation" className="img-fluid border border-2 border-secondary rounded shadow"/>

          <p className="mt-2">
            Store the token as a GitHub secret at{" "}
            <span className="badge text-bg-secondary">
          https://github.com/<strong>USER_OR_ORG</strong>/
          <strong>PROJECT</strong>/settings/secrets/actions
        </span>
            . Use the variable name <div className="badge text-bg-secondary">NYRKIO_JWT_TOKEN</div>.
          </p>
        </div>
      </div>

    </div>
  );
};

const Credits = () => {
  return (
    <div className="text-center">
      <h2 className="text-secondary">Credits</h2>
      <p>
        The <tt><strong className="badge text-bg-secondary">nyrkio/change-detection</strong></tt> GitHub Action is based on{" "}
        <a href="https://github.com/benchmark-action/github-action-benchmark">
          benchmark-action/github-action-benchmark
        </a>
        , which provides the framework parsing logic for pytest-benchmark,
        Google Benchmark, Catch2, and other frameworks.
      </p>
      <p>
        The change point detection algorithm is powered by{" "}
        <a href="https://otava.apache.org">Apache Otava (incubating)</a>,
        originally developed by the performance teams at MongoDB and DataStax.
      </p>
    </div>
  );
};
