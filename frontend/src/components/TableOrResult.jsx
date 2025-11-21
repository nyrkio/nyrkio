import { OrigTestList, TestList, SingleResultWithTestname } from "./Dashboard";
import { createShortNames } from "../lib/utils";
import { Breadcrumb } from "./Breadcrumb";
import { AllChangePoints } from "./AllChangePoints";

const Loading = ({loading}) => {
  if (loading) {
    return (<><div>Loading...</div></>);
  }
  return (<><div className="loading_done"></div></>);
};

// Decide whether we should display a table of test names or a single result.
// If the current url includes a pathname that we match exactly in data
// then we should display that result.
//
// Otherwise, treat the pathname as a prefix for a name in data and list
// all tests with that prefix upto the next "/".
export const TableOrResult = ({ prefix, data, baseUrls, dashboardType, embed, loading, setLoading,summaries,setSummaries,singleTestName, graphName, redraw }) => {
  const testNames = data;
  const shortNames = createShortNames(prefix, testNames);
  const displayNames = shortNames.map((name)=>decodeURIComponent(name));

//    console.debug(singleTestName);
//    console.debug(prefix);
//    console.debug(data);
//    console.debug(baseUrls);

  // If we found an exact match, display the result
  if (data.includes(prefix) || singleTestName) {
    var path = decodeURIComponent(prefix).replace("https://github.com/", "");
    path = path || singleTestName;

    return (
      <>
        <SingleResultWithTestname
          testName={path}
          graphName={graphName}
          baseUrls={baseUrls}
          breadcrumbName={prefix}
          dashboardType={dashboardType}
          embed={embed}
          loading={loading}
          setLoading={setLoading}
          setSummaries={setSummaries}
          summaries={summaries}
          redraw={redraw}
        />
      </>
    );
  } else {
    // Otherwise, display a list of tests upto the next "/"
    return (
      <>
        {embed == "yes" ? "" :
        <Breadcrumb testName={prefix} baseUrls={baseUrls} />
        }
          <AllChangePoints
            testNamePrefix={prefix}
            baseUrls={baseUrls}
            dashboardType={dashboardType}
            />
          <OrigTestList
            baseUrls={baseUrls}
            testNames={testNames}
            shortNames={shortNames}
            displayNames={displayNames}
            prefix={prefix}
            dashboardType={dashboardType}
            embed={embed}

            loading={loading}
            setLoading={setLoading}
            setSummaries={setSummaries}
            summaries={summaries}
            />
      </>
    );
  }
};
