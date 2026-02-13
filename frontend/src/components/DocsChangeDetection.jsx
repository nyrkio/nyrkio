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
      <div className="row mt-4 m-2 p-0 col-lg-10 nyrkio-docs">
        <Intro />
        <TokenSetup />
        <MarkdownRenderer content={contentAction} />
        <Credits />
      </div>
    </>
  );
};

const Intro = () => {
  return (
    <div>
      <h1>Change Point Detection</h1>

      <p>
        Nyrkio Change Detection automatically finds performance regressions and
        improvements in your benchmark history. When a change is detected,
        Nyrkio can notify you via a GitHub issue or Slack message.
      </p>

      <p>
        The easiest way to use Change Detection is the{" "}
        <a href="https://github.com/marketplace/actions/nyrkio-change-detection">
          <code>nyrkio/change-detection@v2</code>
        </a>{" "}
        GitHub Action. It parses output from common benchmark frameworks and
        uploads results to nyrkio.com for analysis.
      </p>

      <p>
        For non-GitHub CI systems, see the{" "}
        <Link to="/docs/getting-started-http">HTTP API documentation</Link>.
      </p>

      <h2>1. Create a JWT token</h2>
    </div>
  );
};

const TokenSetup = () => {
  return (
    <div>
      <p>
        To upload results to the Nyrkio API, you need a JWT token. Click on the
        user menu (top right) and select <strong>User Settings</strong>.
      </p>

      <img src={img3} alt="User settings menu" />
      <p>Create a new API key and save it somewhere secure.</p>

      <img src={img4} alt="API key creation" />

      <p>
        Store the token as a GitHub secret at{" "}
        <code>
          https://github.com/<strong>USER_OR_ORG</strong>/
          <strong>PROJECT</strong>/settings/secrets/actions
        </code>
        . Use the variable name <code>NYRKIO_JWT_TOKEN</code>.
      </p>

      <h2>2. Add the GitHub Action</h2>
    </div>
  );
};

const Credits = () => {
  return (
    <div className="mt-5 pt-4">
      <h3>Credits</h3>
      <p>
        The <tt><strong>nyrkio/change-detection</strong></tt> GitHub Action is based on{" "}
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
