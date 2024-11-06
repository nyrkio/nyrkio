import { Breadcrumb, TestList, SingleResultWithTestname } from "./Dashboard";
import { createShortNames } from "../lib/utils";

// Decide whether we should display a table of test names or a single result.
// If the current url includes a pathname that we match exactly in data
// then we should display that result.
//
// Otherwise, treat the pathname as a prefix for a name in data and list
// all tests with that prefix upto the next "/".
export const TableOrResult = ({ prefix, data, baseUrls, dashboardType, embed }) => {
  const testNames = data;
  const shortNames = createShortNames(prefix, testNames);

  // If we found an exact match, display the result
  if (data.includes(prefix)) {
    var path = decodeURIComponent(prefix).replace("https://github.com/", "");

    return (
      <>
        <SingleResultWithTestname
          testName={path}
          baseUrls={baseUrls}
          breadcrumbName={prefix}
          dashboardType={dashboardType}
          embed={embed}
        />
      </>
    );
  } else {
    console.debug("data: " + data);
    // Otherwise, display a list of tests upto the next "/"
    return (
      <>
        {embed == "yes" ? "" :
        <Breadcrumb testName={prefix} baseUrls={baseUrls} />
        }
        <div className="col-md-7">
          <TestList
            baseUrls={baseUrls}
            testNames={data}
            shortNames={shortNames}
            displayNames={shortNames.map((name) => decodeURIComponent(name))}
            prefix={prefix}
          />
        </div>
      </>
    );
  }
};
