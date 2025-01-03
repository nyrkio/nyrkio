import { AgGridReact } from "ag-grid-react"; // React Grid Logic
import "ag-grid-community/styles/ag-grid.css"; // Core CSS
import "ag-grid-community/styles/ag-theme-quartz.css"; // Theme
import { formatCommit, parseTimestamp } from "../lib/utils";
import React, { StrictMode, useCallback, useMemo, useRef, foo } from "react";

const Loading = ({loading}) => {
  if (loading) {
    return (<><div className="loading">Loading...</div></>);
  }
  return (<><div className="loading_done"></div></>);
};

export const ChangePointSummaryTable = ({ changeData, queryStringTextTimestamp, loading }) => {
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
    if (loading) {
      return (<Loading loading={loading} />);
    }
    return (
      <>
        <span className="no-changepoints">(no changepoints)</span>
      </>
    );
  }

  const colDefs = [
    { field: "date", sort: "desc",
      cellRenderer: (params) => {
        const text = params.value;
        if (text == queryStringTextTimestamp){
          return (<b>{text}</b>);
        }
        return text;
      }
    },
    { field: "metric",
      cellRenderer: (params) => {
        const metric_name = params.value;
        const url = "#"+metric_name;
        return (
          <a href={url}>{metric_name}</a>
        );
      }
    },
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
        <h3>Performance Changes</h3>
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
