import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import { Link } from "react-router-dom";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import introDoc from "../docs/intro.md";
import introDocAction from "../docs/intro-action.md";
import img1 from "../static/getting-started-login-button.png";
import img2 from "../static/getting-started-login.png";
import img3 from "../static/getting-started-UserSettings.png";
import img4 from "../static/getting-started-API-key.png";
import gh_permissions_img from "../static/github_permissions.png";

export const Docs = () => {
  const [content, setContent] = useState("");
  const [contentAction, setContentAction] = useState("");

  useEffect(() => {
    fetch(introDoc)
      .then((response) => response.text())
      .then((text) => {
        setContent(text);
      });
    fetch(introDocAction)
      .then((response) => response.text())
      .then((text) => {
        setContentAction(text);
      });
  });


  return (
    <>
      <div className="row mt-4 m-2 p-0 col-lg-10">
        <FirstHalf />
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          children={contentAction}
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
        <hr className="mt-5 mb-5" />
        <h2>Using Nyrkiö with curl HTTP requests</h2>
        <p>Alternatively, if you don't use GitHub or GitHub actions for Continuous Integration,
           below is a tutorial using generic HTTP requests with <code>curl</code>:</p>
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

const FirstHalf = () => {
  return (
    <>
      <div>
        <h1> Getting started in 3 easy steps</h1>

        <p>
          The easiest way to use Nyrkiö Change Detection on GitHub is to add the <a
          href="https://github.com/marketplace/actions/nyrkio-change-detection"><code>nyrkio/change-detection@v2</code></a> GitHub
          action to your workflows.
        </p>
        <p>
          Alternatively, you can use the HTTP API directly. <a href="curl">See
          below for a generic <code>curl</code> example</a>.
        </p>

        <h2> 1. Install the Nyrkiö app on GitHub</h2>

        <p><a href="https://github.com/apps/nyrkio/installations/new">Click here to install
          Nyrkiö on GitHub.</a>
        </p>
        <p>GitHub will ask to grant Nyrkiö the following permissions:</p>
            <img src={gh_permissions_img} alt="Github permissions dialog" />
            <p>You can choose to not grant any one of those permissions. Nyrkiö will
            continue to work without the particular feature.
        </p>

        <p>
          When you are done with the GitHub permissions and installation screens, you are redirected
          back to nyrkio.com. You should be logged in to your new Nyrkiö user account now.</p>

        <h2> 2. Create a JWT token</h2>
        <p>
          We use JWT to access the Nyrkiö API. Click again on the red button on
          your top right. If you are logged in you can now select _User
          Settings_.
        </p>

        <img src={img3} />
        <p>
          Create a new API key and make sure to copy paste it and save it
          somewhere.
        </p>

        <img src={img4} />

        <p>Now head to <code>https://github.com/<strong>USER_OR_ORG</strong>/<strong>PROJECT</strong>/settings/secrets/actions</code>
           Store the token you just created either as a <em>Environment secret</em> or <em>Repository secret</em>. We'll use then
           variable name <code>NYRKIO_JWT_TOKEN</code> for it below.
        </p>

      </div>
    </>
  );
};

const FirstHalfCurl = () => {
  return (
    <>
      <div>
        <h2> 1.Create a user account</h2>

        <p>Click on the Login button in the top right corner:</p>

        <img src={img1} />

        <p>
          Choose between GitHub OAuth or traditional username + password logins.
        </p>

        <img src={img2} />

        <h2> 2. Create a JWT token</h2>

        <p>
          We use JWT to access the Nyrkiö API. Click again on the red button on
          your top right. If you are logged in you can now select _User
          Settings_.
        </p>

        <img src={img3} />
        <p>
          Create a new API key and make sure to copy paste it and save it
          somewhere.
        </p>

        <img src={img4} />
      </div>
    </>
  );
};
