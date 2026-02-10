import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import { Link } from "react-router-dom";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import introDocRunners from "../docs/intro-runners.md";
import gh_permissions_img from "../static/github_permissions.png";
import select1before from "../static/runner/turso_select1_ghrunner.png";
import select1after from "../static/runner/turso_select1_nyrkiorunner.png";

export const Docs = () => {
  const [contentRunners, setContentRunners] = useState("");

  useEffect(() => {
    fetch(introDocRunners)
      .then((response) => response.text())
      .then((text) => {
        setContentRunners(text);
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
        <SetupSteps />
        <MarkdownRenderer content={contentRunners} />
      </div>
    </>
  );
};

const SetupSteps = () => {
  return (
    <div>
      <h1 id="getting-started">Getting started with Nyrkio Runners</h1>

      <p>
        Nyrkio Runners are GitHub-hosted runners configured for{" "}
        <strong>stable, repeatable benchmark results</strong>. Unlike standard
        GitHub runners, Nyrkio runners eliminate environmental noise that causes
        benchmark variation.
      </p>

      <div className="row my-4">
        <div className="col-md-6">
          <p className="text-center"><strong>Standard GitHub Runner</strong></p>
          <img
            src={select1before}
            alt="Noisy benchmark results on standard GitHub runner"
            style={{ width: "100%", border: "1px solid #ddd", borderRadius: "4px" }}
          />
          <p className="text-center text-muted">Noise range: ~75%</p>
        </div>
        <div className="col-md-6">
          <p className="text-center"><strong>Nyrkio Runner</strong></p>
          <img
            src={select1after}
            alt="Stable benchmark results on Nyrkio runner"
            style={{ width: "100%", border: "1px solid #ddd", borderRadius: "4px" }}
          />
          <p className="text-center text-muted">Noise range: ~5%</p>
        </div>
      </div>
      <p className="text-center">
        <em>Some pilot customers achieved a min-max range of noise that was less than 1 ns!</em>
      </p>

      <h2>1. Install the Nyrkio app on GitHub</h2>

      <p>
        <a href="https://github.com/apps/nyrkio/installations/new">
          Click here to install Nyrkio on GitHub.
        </a>
      </p>
      <p>GitHub will ask to grant Nyrkio the following permissions:</p>
      <img src={gh_permissions_img} alt="Github permissions dialog" />
      <p>
        You can choose to not grant any one of those permissions. Nyrkio will
        continue to work without the particular feature.
      </p>

      <p>
        <strong>Note:</strong> For 3rd party runners, we recommend creating a
        separate GitHub org for the repositories you want to use Nyrkiö with.
        For repositories in your personal namespace, using 3rd party test runners
        requires admin rights to the repo, while github orgs have a separate permission
        for this functionality.
      </p>

      <h2>2. Select a subscription</h2>
      <p>
        Head to <Link to="/pricing">Pricing</Link> and select a plan. For
        getting started, the <strong>CPU-Hours</strong> plan is
        consumption-based: you only pay for the minutes you use.
      </p>
    </div>
  );
};
