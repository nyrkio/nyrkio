import { Link, useLocation } from "react-router-dom";

export const Breadcrumb = ({ testName, baseUrls }) => {
  if (testName === undefined) {
    return <></>;
  }

  const createItems = () => {
    return testName.split("/").map((name, i) => {
      // Check if we're the last component
      if (i === testName.split("/").length - 1) {
        return (
          <li className="breadcrumb-item active" aria-current="page" key="leaf">
            {decodeURIComponent(name).replace("https://github.com/", "")}
          </li>
        );
      }

      var prefix = testName
        .split("/")
        .slice(0, i + 1)
        .join("/");
      return (
        <li className="breadcrumb-item" key={prefix}>
          <Link to={`/${baseUrls.tests}/${prefix}`}>
            {decodeURIComponent(name).replace("https://github.com/", "")}
          </Link>
        </li>
      );
    });
  };

  console.debug("baseUrls: " + baseUrls.testRoot);

  return (
    <>
      <nav className="navbar col-xs-12 col-lg-11 col-xl-10">
        <div className="container-fluid breadcrumb-wrapper">
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb">
              {baseUrls.breadcrumbTestRootTitle ? (
                <li className="breadcrumb-item" key="root">
                  <em>
                  <Link to={`${baseUrls.testRoot}`}>
                    {baseUrls.breadcrumbTestRootTitle}
                  </Link>
                  </em>
                </li>
              ) : (
                <span></span>
              )}
              {createItems()}
            </ol>
          </nav>
        </div>
      </nav>
    </>
  );
};
