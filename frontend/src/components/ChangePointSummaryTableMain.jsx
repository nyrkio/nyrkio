import { AgGridReact } from "ag-grid-react"; // React Grid Logic
import "ag-grid-community/styles/ag-grid.css"; // Core CSS
import "ag-grid-community/styles/ag-theme-quartz.css"; // Theme
import { formatCommit, parseTimestamp } from "../lib/utils";
import React, { StrictMode, useCallback, useMemo, useRef, foo } from "react";

const Loading = ({loading}) => {
  if (loading) {
    return (<><div className="loading summary-table">Loading...</div></>);
  }
  return (<><div className="loading_done"></div></>);
};

export const ChangePointSummaryTableMain = ({ title, changeData, baseUrls, queryStringTextTimestamp, loading, metricsData }) => {
  var rowData = [];

  const directionMap = {};
  if(Array.isArray(metricsData)){
    metricsData.forEach((m)=>directionMap[m.name]=m.direction);
  }
  const direction = (metric)=>{
      if(directionMap[metric]){
        return directionMap[metric];
      }
      return null;
  };
  const directionFormatter = (value, metric) => {
    let d = direction(metric);
    if ( d == "higher_is_better"){
      if (value>0){
        return (<span className="bg-success nyrkio-change nyrkio-change-improvement">{value}</span>);
      }
      if (value<0){
        return (<span className="bg-danger nyrkio-change nyrkio-change-regression">{value}</span>);
      }
      // Should not be possible!
      return (<span className="nyrkio-change nyrkio-change-neutral">{value}</span>);
    }
    if ( d == "lower_is_better"){
      if (value<0){
        return (<span className="bg-success nyrkio-change nyrkio-change-improvement">{value}</span>);
      }
      if (value>0){
        return (<span className="bg-danger nyrkio-change nyrkio-change-regression">{value}</span>);
      }
      // Should not be possible!
      return (<span className="bg-success nyrkio-change nyrkio-change-neutral">{value}</span>);
    }
    return (<span className="nyrkio-change nyrkio-change-unknown">{value}</span>);
  };
  const directionColor = (value, metric) => {
    let d = direction(metric);
    if ( d == "higher_is_better"){
      if (value>0){
        return "#00ff0055";
      }
      if (value<0){
        return "#ff000055";
      }
      // Should not be possible!
      return "none";
    }
    if ( d == "lower_is_better"){
      if (value<0){
        return "#00ff0055";
      }
      if (value>0){
        return "#ff000055";
      }
      // Should not be possible!
      return "#fffff00";
    }
    return "#ffffff00";
  };
  const directionArrow = (metric) => {
      if (directionMap[metric]=="higher_is_better") return <span title="higher is better">⇧</span>;
      if (directionMap[metric]=="lower_is_better") return <span title="lower is better">⇩</span>;
  }

  console.debug(changeData);
  Object.entries(changeData).forEach(([shortName, obj]) => {
    obj.forEach((changePoint) => {
        console.debug(changePoint);
        const branchName = changePoint["attributes"]["branch"]
        const test_name = changePoint["test_name"];
        const changes = changePoint["cp_values"];
        console.debug(changes);
        changes.map((change) => {
          const commit = changePoint["_id"]["git_commit"];

          let commit_msg = "";
          if (changePoint["attributes"].hasOwnProperty("commit_msg")) {
            commit_msg = changePoint["attributes"]["commit_msg"];
          }

          const repo = changePoint["attributes"]["git_repo"];
          const changeValue = Math.round(change["forward_change_percent"]*100)/100;
          const metric_name = change["metric"];
          rowData.push({
            date: parseTimestamp(changePoint["time"]),
            commit: { commit, commit_msg, repo },
            test: { test_name, branchName },
            metric: { test_name, metric_name, branchName },
            change: { changeValue, metric_name }
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
    { field: "test",
      cellRenderer: (params) => {
        let test_name = params.value.test_name;
        const branchName = params.value.branchName;
        let url = baseUrls.resultsWithOrg + "/" + test_name;
        console.log(baseUrls);
        if (baseUrls.results=="/public"){
          url = baseUrls.resultsWithOrg + "/" + branchName + "/" + test_name;
        }

        if(test_name.length>12){
          test_name = "..." + test_name.substring(-12);
        }
        return (
          <>
          <a href={url}>{test_name}</a>
          </>
        );
      },
      valueFormatter: (params)=>{
        return params.value.test_name;
      },
    },
    { field: "metric",
      cellRenderer: (params) => {
        const metric_name = params.value.metric_name;
        const test_name = params.value.test_name;
        const url = baseUrls.resultsWithOrg + "/" + test_name +"#"+ metric_name;
        return (
          <>
          <a href={url}>{metric_name}</a> {directionArrow(metric_name)}
          </>
        );
      },
      valueFormatter: (params)=>{
        return params.value.metric_name;
      },
    },
    { field: "change",
      cellRenderer: (params) => {
        const { changeValue, metric_name } = params.value;
        // const d = directionFormatter(changeValue, metric_name);
        return (<>{changeValue} %</>);
      },
      cellStyle: (params) => {
        const { changeValue, metric_name } = params.value;
        const d = directionColor(changeValue, metric_name);
        return {backgroundColor:d};
      },
      valueFormatter: (params)=>{
        return params.value.change_value;
      },
    },
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
      valueFormatter: (params)=>{
        return params.value.commit;
      },
    },
  ];

  const autoSizeStrategy = useMemo(() => {
    return {
      type: "fitGridWidth",
    };
  });

  return (
    <>
      <div className="row text-center">
        <h3>{title?title:"Performance Changes"}</h3>
      </div>
      <div
        className="ag-theme-quartz ag-theme-nyrkio pb-5 col-sm-12 col-lg-12 col-xl-12"
        style={{ height: 500, width: "100%" }}
      >
        <AgGridReact
          rowData={rowData}
          columnDefs={colDefs}
          pagination={true}
          autoSizeStrategy={autoSizeStrategy}
          style={{width: "100%"}}
          className="w-100"
        />
      </div>
    </>
  );
};
