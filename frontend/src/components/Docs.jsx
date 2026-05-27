import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import { Link } from "react-router-dom";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import introDocRunners from "../docs/intro-runners.md";
import gh_permissions_img from "../static/github_permissions.png";
import select1before from "../static/runner/turso_select1_ghrunner.png";
import select1after from "../static/runner/turso_select1_nyrkiorunner.png";
import {HighlightLoginSection} from "./HighlightLoginSection.jsx";

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
      <div className="container">
        <SetupSteps />
        <div className="text-center markdown-container">
          <MarkdownRenderer content={contentRunners} />
        </div>
      </div>
    </>
  );
};

const SetupSteps = () => {
  return (
    <div >
      <h1 id="getting-started" className="text-primary text-center mb-4 mb-md-5">Getting started with Nyrkio Runners</h1>

      <p className="text-center mx-auto" style={{maxWidth: "1000px"}}>
        Nyrkio Runners are GitHub-hosted runners configured for <strong>stable, repeatable benchmark results</strong>. Unlike standard GitHub runners, Nyrkio runners eliminate environmental noise that causes benchmark variation.
      </p>

      <div className="row my-4">
        <div className="col-md-6">
          <p className="text-center">
            <strong className="text-secondary">Standard GitHub Runner</strong>
          </p>
          <img
            className="img-fluid border border-2 border-secondary rounded shadow"
            src={select1before}
            alt="Noisy benchmark results on standard GitHub runner"
            width="1221"
            height="319"
          />
          <p className="text-center text-muted mt-3">Noise range: ~75%</p>
        </div>
        <div className="col-md-6">
          <p className="text-center">
            <strong className="text-secondary">Nyrkio Runner</strong>
          </p>
          <img
            className="img-fluid border border-2 border-secondary rounded shadow"
            src={select1after}
            alt="Stable benchmark results on Nyrkio runner"
            width="1221"
            height="319"
          />
          <p className="text-center text-muted mt-3">Noise range: ~5%</p>
        </div>
      </div>
      <p className="text-center">
        <strong>Some pilot customers achieved a min-max range of noise that was less than 1 ns!</strong>
      </p>

      <h2 className="h3 text-secondary text-center mt-section">1. Install the Nyrkio app on GitHub</h2>
      <p className="text-center my-4 my-md-6">
        <a href="https://github.com/apps/nyrkio/installations/new" className="btn btn-outline-primary w-100 w-md-auto">Github.com</a>
      </p>

      <div className="row">
        <HighlightLoginSection maxWidth="1160px">
          <div className="row align-items-center py-md-3">
            <div className="col-md-6">
              <p>GitHub will ask to grant Nyrkio the following permissions:</p>
              <img className="img-fluid bg-white p-4 rounded shadow border border-2 border-secondary"
                   src={gh_permissions_img} alt="Github permissions dialog" />
            </div>
            <div className="col-md-6">
              <p>You can choose to not grant any one of those permissions. Nyrkio will continue to work without the particular feature.</p>
              <div className="bg-white p-4 rounded shadow border border-2 border-secondary">
                <strong className="d-block mb-2">Note:</strong>
                For 3rd party runners, we recommend creating a
                separate GitHub org for the repositories you want to use Nyrkiö with.
                For repositories in your personal namespace, using 3rd party test runners
                requires admin rights to the repo, while github orgs have a separate permission
                for this functionality.
              </div>
            </div>

          </div>
        </HighlightLoginSection>
      </div>

      <hr className="my-4 my-md-6" />

      <div className="text-center">
        <h2 className="h3 text-secondary mb-4">2. Select a subscription</h2>
        <p>For getting started, the CPU-Hours plan is consumption-based: you only pay for the minutes you use</p>
        <div>
          <a className="btn btn-outline-primary mt-4 mt-md-5 w-100 w-md-auto" href="/pricing">See all pricing</a>
        </div>
      </div>

      <hr className="my-4 my-md-6"/>
    </div>
  );
};
