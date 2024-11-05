import { AgGridReact } from "ag-grid-react"; // React Grid Logic
import "ag-grid-community/styles/ag-grid.css"; // Core CSS
import "ag-grid-community/styles/ag-theme-quartz.css"; // Theme
import { formatCommit, parseTimestamp } from "../lib/utils";
import React, { StrictMode, useCallback, useMemo, useRef, foo } from "react";

export const ChangePointSummaryTable = ({ changeData }) => {
  var rowData = [];

  console.debug(changeData);
  Object.entries(changeData).forEach(([testName, value]) => {
    value.forEach((changePoint) => {
      console.debug(changePoint);
      const changes = changePoint["changes"];
      console.debug(changes);
      changes.map((change) => {
        const commit = changePoint["attributes"]["git_commit"];

        let commit_msg = "";
        if (changePoint["attributes"].hasOwnProperty("commit_msg")) {
          commit_msg = changePoint["attributes"]["commit_msg"];
        }

        const repo = changePoint["attributes"]["git_repo"];
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
    return (
      <>
        <span className="no-changepoints">(no changepoints)</span>
      </>
    );
  }

  const colDefs = [
    { field: "date", sort: "desc" },
    { field: "metric" },
    { field: "change" },
    {
      field: "commit",
      cellRenderer: (params) => {
        const { commit, commit_msg, repo } = params.value;

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

  const autoSizeStrategy = useMemo(() => {
    return {
      type: "fitCellContents",
    };
  });

  return (
    <>
      <div className="row text-center">
        <h4>Performance Changes</h4>
      </div>
      <div
        className="ag-theme-quartz ag-theme-nyrkio pb-5"
        style={{ height: 500, width: "90%" }}
      >
        <AgGridReact
          rowData={rowData}
          columnDefs={colDefs}
          pagination={true}
          autoSizeStrategy={autoSizeStrategy}
        />
      </div>
    </>
  );
};
