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
          <img src={img1} style={{width:"1px", "maxHeight":"1px"}}/>
          <img src={img2} style={{width:"1px", "maxHeight":"1px"}}/>
          <img src={img3} style={{width:"1px", "maxHeight":"1px"}}/>
          <img src={img4} style={{width:"1px", "maxHeight":"1px"}}/>
          </div>
    </>
  );
};
