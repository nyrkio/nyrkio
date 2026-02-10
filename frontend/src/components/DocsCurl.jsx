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
      <div className="row mt-4 m-2 p-0 col-lg-10">
        <h1>Using the Nyrkio HTTP API</h1>
        <p>
          For CI systems other than GitHub Actions, or for custom integrations,
          you can use the Nyrkio REST API directly. This tutorial shows how to
          upload benchmark results using <code>curl</code>.
        </p>
        <p>
          For GitHub users, see the{" "}
          <a href="/docs/getting-started">Getting started guide</a> for the
          easier approach using Nyrkio Runners and the change-detection action.
        </p>
        <FirstHalfCurl />
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
    </>
  );
};

const FirstHalfCurl = () => {
  return (
    <>
      <div>
        <h2 id="getting-started-curl">1. Create a user account</h2>

        <p>Click on the Login button in the top right corner:</p>

        <img src={img1} alt="Login button" />

        <p>
          Choose between GitHub OAuth or traditional username + password logins.
        </p>

        <img src={img2} alt="Login options" />

        <h2>2. Create a JWT token</h2>

        <p>
          We use JWT to access the Nyrkio API. Click on the user menu (top
          right) and select <strong>User Settings</strong>.
        </p>

        <img src={img3} alt="User settings menu" />
        <p>Create a new API key and save it somewhere secure.</p>

        <img src={img4} alt="API key creation" />
      </div>
    </>
  );
};
