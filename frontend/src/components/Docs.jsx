import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import { Link } from "react-router-dom";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import introDoc from "../docs/intro.md";
import img1 from "../static/getting-started-login-button.png"
import img2 from "../static/getting-started-login.png"
import img3 from "../static/getting-started-UserSettings.png"
import img4 from "../static/getting-started-API-key.png"

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
        <div className="row mt-4 m-2 p-0 col-lg-10">
        <FirstHalf />
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
      This guide will show you how to get started with Nyrkiö.
      </p>

      <p>
      All of the examples in this doc use `curl` but you can use your favourite language and libraries for sending HTTP requests.
      </p>

      <h2> 1.Create a user account</h2>

      <p>
      Click on the Login button in the top right corner:
      </p>

          <img src={img1} />

      <p>
      The easiest and recommended option is to just click on the Github button on the top and you're done.
      </p>

          <img src={img2} />

      <h2> 2. Create a JWT token</h2>

      <p>
      We use JWT to access the Nyrkiö API. Click again on the red button on your top right. If you are
      logged in you can now select _User Settings_.
      </p>

          <img src={img3} />
      <p>
      Create a new API key and make sure to copy paste it and save it somewhere.
      </p>

          <img src={img4} />


      </div>
    </>
  );

};
