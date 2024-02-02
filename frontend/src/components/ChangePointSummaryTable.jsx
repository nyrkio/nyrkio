import { AgGridReact } from "ag-grid-react"; // React Grid Logic
import "ag-grid-community/styles/ag-grid.css"; // Core CSS
import "ag-grid-community/styles/ag-theme-quartz.css"; // Theme
import { formatCommit, parseTimestamp } from "../lib/utils";

export const ChangePointSummaryTable = ({ changeData }) => {
  var rowData = [];

  Object.entries(changeData).forEach(([testName, value]) => {
    value.forEach((changePoint) => {
      console.log(changePoint);
      const changes = changePoint["changes"];
      console.log(changes);
      changes.map((change) => {
        const commit = changePoint["attributes"]["git_commit"][0];

        let commit_msg = "";
        if (changePoint["attributes"].hasOwnProperty("commit_msg")) {
          commit_msg = changePoint["attributes"]["commit_msg"][0];
        }

        const repo = changePoint["attributes"]["git_repo"][0];
        rowData.push({
          date: parseTimestamp(changePoint["time"]),
          commit: { commit, commit_msg, repo },
          metric: change["metric"],
          change: change["forward_change_percent"] + "%",
        });
      });
    });
  });

  if (rowData.length === 0) {
    return <></>;
  }

  const colDefs = [
    { field: "date" },
    { field: "metric" },
    { field: "change" },
    {
      field: "commit",
      cellRenderer: (params) => {
        const { commit, commit_msg, repo } = params.value;

        // If we failed to lookup the commit message, display the commit sha
        if (commit_msg === "") {
          return commit;
        }

        const url = repo + "/commit/" + commit;
        const text = formatCommit(commit, commit_msg);
        return (
          <a href={url} target="_blank">
            {text}
          </a>
        );
      },
    },
  ];

  return (
    <>
      <div className="row text-center">
        <h4>Performance Changes</h4>
      </div>
      <div className="ag-theme-quartz pb-5" style={{ height: 500, width: 900 }}>
        <AgGridReact rowData={rowData} columnDefs={colDefs} pagination={true} />
      </div>
    </>
  );
};
