import { AgGridReact } from "ag-grid-react"; // React Grid Logic
import "ag-grid-community/styles/ag-grid.css"; // Core CSS
import "ag-grid-community/styles/ag-theme-quartz.css"; // Theme
import { formatCommit, parseTimestamp } from "../lib/utils";
import React, { StrictMode, useCallback, useMemo, useRef, foo } from "react";
import { commitUrl } from "../lib/github";

const Loading = ({loading}) => {
  if (loading) {
    return (<><div className="loading summary-table">Loading...</div></>);
  }
  return (<><div className="loading_done"></div></>);
};

export const ChangePointSummaryTableMain = ({ title, changeData, baseUrls, queryStringTextTimestamp, loading, metricsData, isPublicDashboard }) => {
  var rowData = [];
  const directionMap = {};
  if(Array.isArray(metricsData)){
    metricsData.forEach((m)=>directionMap[m.name]=m.direction);
  }
  let isLeafDashboard = false;

  const direction = (metric,changePoint)=>{
      if(changePoint && changePoint.metric && changePoint.metric[metric] && changePoint.metric[metric].direction){
        return changePoint.metric[metric].direction;
      }
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
  let previousRow = null;
  Object.entries(changeData).forEach(([shortName, obj]) => {
    obj.forEach((changePoint) => {
        // console.debug(changePoint);
        if(changePoint["_id"]){
            changePoint["commit"] = changePoint["_id"]["git_commit"];
        } else {
            changePoint["commit"] = changePoint["attributes"]["git_commit"];
        }


        const branchName = changePoint["attributes"]["branch"]
        let test_name = changePoint["test_name"];
        const changes = changePoint["cp_values"] || changePoint["changes"];
        changes.map((change) => {
          let commit_msg = "";

          const commit = changePoint["commit"];
          if (changePoint["attributes"].hasOwnProperty("commit_msg")) {
            commit_msg = changePoint["attributes"]["commit_msg"];
          }

          const repo = changePoint["attributes"]["git_repo"];
          const changeValue = Math.round(change["forward_change_percent"]*100)/100;
          const metric_name = change["metric"];
          const date = parseTimestamp(changePoint["time"]);

          const isSame = {date:false, commit: false, test: false, index: 0 };
          if (previousRow !== null){
            isSame.date = (previousRow.date == date);
            isSame.commit = (previousRow["commit"] == changePoint["commit"]);
            isSame.test = (previousRow["test_name"] == test_name);
          }
          if (isSame.date && isSame.commit){
            changePoint["__isSameIndex"] = 1 + (previousRow["__isSameIndex"] === undefined ? 0 : previousRow["__isSameIndex"]);
            isSame.index += changePoint["__isSameIndex"];
          }
          //console.log(changePoint["__isSameIndex"] + JSON.stringify(changePoint["_id"]));
          if(test_name){
            rowData.push({
              date: { date, isSame },
              commit: { commit, commit_msg, repo, isSame },
              test: { test_name, branchName, isSame },
              metric: { test_name, metric_name, branchName },
              change: { changeValue, metric_name }
            });
          } else {
            rowData.push({
              date: { date, isSame },
              commit: { commit, commit_msg, repo, isSame },
              test: { branchName, isSame },
              metric: { metric_name, branchName },
              change: { changeValue, metric_name }
            });
            isLeafDashboard=true;
          }
          previousRow = changePoint;
          previousRow.date = date;
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

  let colDefs = [
    { field: "date", sort: "desc",
      cellRenderer: (params) => {
        const text = params.value.date;
        const isSame = params.value.isSame;
        if (text == queryStringTextTimestamp){
          return (<b>{text}</b>);
        }
        if (params.column.sort != "desc"){
          isSame.userSort = true;
        }
        if (isSame.date && params.column.sort == "desc") {
          return "";
        }
        else {
          return text;
        }
      },
      valueFormatter: (params)=>{
        return params.value.date;
      },
    },
    { field: "test",
      cellRenderer: (params) => {
        let test_name = params.value.test_name;
        const branchName = params.value.branchName;
        const isSame = params.value.isSame;
        let url = baseUrls.resultsWithOrg + "/" + test_name;
        // console.log(baseUrls);
        if (baseUrls.results=="/public"){
          url = baseUrls.resultsWithOrg + "/" + branchName + "/" + test_name;
        }

        if (isSame.date && isSame.test && ! isSame.userSort) {
          return "";
        }
        else {
          return (
            <>
            <a href={url}>{test_name}</a>
            </>
          );
        }
      },
      valueFormatter: (params)=>{
        return params.value.test_name;
      },
    },
    { field: "metric",
      cellRenderer: (params) => {
        const metric_name = params.value.metric_name;
        const test_name = params.value.test_name;
        const branchName = params.value.branchName;
        let url = baseUrls.resultsWithOrg + "/" + test_name +"#"+ metric_name;
        if (baseUrls.results=="/public"){
          url = baseUrls.resultsWithOrg + "/" + branchName + "/" + test_name +"#"+ metric_name;
        }
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
        const isSame = params.value.isSame;

        const url = commitUrl(repo, commit);
        const text = formatCommit(commit, commit_msg);
        if (isSame.date && isSame.commit && ! isSame.userSort) {
          return "";
        }
        else {
          return (
            <a href={url} target="_blank">
              {text}
            </a>
          );
        }
      },
      valueFormatter: (params)=>{
        return params.value.commit;
      },
    },
  ];

  if(isLeafDashboard){
    colDefs = [colDefs[0], colDefs[2], colDefs[3], colDefs[4] ]
  }
  const autoSizeStrategy = useMemo(() => {
    return {
      type: "fitCellContents",
    };
  });

  const rowClassRules = {
      'ag-row-is-same': (params) => {
        // console.log(params);
        const isSame = params.data.date.isSame;
        return isSame.date && isSame.commit;
      },
      'ag-row-is-new': (params) => {
            console.log(params.data.date);
        const isSame = params.data.date.isSame;
        return ! (isSame.date && isSame.commit);
      }
  };
  const getRowStyle = (params) => {
        const isSame = params.data.date.isSame;
         //console.log(params.data.date);
        if ( (isSame.date && isSame.commit) ){
          const oldh = params.node.rowHeight;
          const h = 42;
          // console.log(isSame);
          const translate = params.node.rowTop -(oldh -h)*(isSame.index+0.5);
          params.node.rowHeight = h;
          return {transform: `translateY(${translate}px)`}
        }
//         else {
//           params.node.rowHeight = 100;
//         }
  }
  const gridHeightPx = 150 + Math.min(Math.max(rowData.length, 2), 20) * 50;
  return (
    <>
      <div className="row text-center">
        <h3>{title?title:"Performance Changes"}</h3>
      </div>
      <div
        className="ag-main-cp-table ag-theme-quartz ag-theme-nyrkio pb-5 col-sm-12 col-lg-12 col-xl-12"
        style={{ width: "100%", height: gridHeightPx, minHeight: "13em", maxHeight: "95vh" }}
      >
        <AgGridReact
          rowData={rowData}
          columnDefs={colDefs}
          pagination={true}
          autoSizeStrategy={autoSizeStrategy}
          style={{width: "100%", maxHeight: "75vhi"}}
          className="w-100"
          paginationPageSize={20}
          paginationPageSizeSelector={[10, 20, 50, 100]}
          getRowClass={getRowStyle}
          rowClassRules={rowClassRules}                                                                                                                                                                                                                                                    />
      </div>
    </>
  );
};
