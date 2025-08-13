import { useEffect, useState } from "react";
import { dashboardTypes, getOrg, getOrgRepoShort, getOrgRepoBranch } from "../lib/utils";


export const Pulls = ({testName, sendSelectedPr, baseUrls, breadcrumbName, dashboardType }) => {
  const [prs, setPrs] = useState([]);
  const [commitsInPr, setCommitsInPr] = useState({});
  const [commitList, setCommitList] = useState([]);
  const [selectedPr, setSelectedPr] = useState();

  let orgEtcPrefix = "";
  let orgRepoBranch = "";
  if(dashboardType == dashboardTypes.ORG) {
    if (breadcrumbName) {
      orgEtcPrefix = getOrg(breadcrumbName);
    }
  }
  if(dashboardType == dashboardTypes.PUBLIC) {
    if (breadcrumbName) {
      orgRepoBranch = getOrgRepoBranch(breadcrumbName) + "/";
      orgEtcPrefix = "/" + getOrgRepoShort(breadcrumbName) + "/";
    }

  }
  const fetchPulls = async () => {

    var url = `${baseUrls.apiRoot}pulls${orgEtcPrefix}`;
    if(dashboardType == dashboardTypes.ORG) {
      url = `${baseUrls.apiRoot}${orgEtcPrefix}/pulls`;
    }
    if(dashboardType == dashboardTypes.PUBLIC) {
      var url = `${baseUrls.apiRoot}pulls/${testName}`;
    }
      console.log(url);
    const response = await fetch(url, {
      headers: {
        "Content-type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    });

    if (response.status != 200) {
      console.error("Failed to fetch pull requests: " + response.status);
      console.log(response);
      return;
    }

    const res = await response.json();
    const filteredPullRequests= [];
    const commits = {};
    for (var o of res) {
      for (var name of o.test_names){
        if (orgRepoBranch + name === testName){
          const key = `${o.git_repo}/pull/${o.pull_number}`;
          if (commits[key] === undefined) {
            commits[key] = [];
            filteredPullRequests.push(key);
          }
          commits[key].push(o.git_commit);
        }
      }
    }
    setPrs(filteredPullRequests), setCommitsInPr(commits);
  };

  const fetchPullResult = async (pr, c) => {
    const [repo, pull_number] = pr.split("/pull/");
    const url = `${baseUrls.apiRoot}pulls/${repo}/${pull_number}/result/${c}/test/${testName}`
    const response = await fetch(url, {
      headers: {
        "Content-type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    });

    if (response.status != 200) {
      console.error(`Failed to fetch pull request ${url} : ${response.status}`);
      console.log(response);
      return;
    }

    const res = await response.json();
    console.log(res);

    const response2 = await fetch(`${baseUrls.apiRoot}pulls/${repo}/${pull_number}/changes/${c}`, {
      headers: {
        "Content-type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    });

    if (response2.status != 200) {
      console.error(`Failed to fetch pull request changes (${pr} ${c}) : ${response.status}`);
      console.log(response2);
      return;
    }
    const res2 = await response2.json();
    sendSelectedPrResults(res2);
  };

  useEffect(() => {
    fetchPulls();
  }, []);


  const prSelected = (pr) => {
    console.debug("prSelected");
    console.log(commitsInPr);
    setSelectedPr(pr);
    const commitPicker = document.getElementById("commitPicker");
    if (pr==0) {
      commitPicker.style.display = "none";
      commitPicker.disabled = true;
      sendSelectedPr(false);
    }
    else if (commitsInPr) {
      const listBuilder = [];
      const seen = [];
      for (var c of commitsInPr[pr]){
        if (seen.includes(c) ) continue;
        seen.push(c);
        listBuilder.push(<option value={c} key={c}>{c.substring(0,9)}</option>);
      }
      setCommitList( listBuilder );
      commitPicker.disabled = false;
      commitPicker.style.display = "inline";
      if(seen.length>0){
        commitSelected(seen[0], pr);
      }
    }
  };


  const commitSelected = (selectedCommit, pr) => {
    if (selectedCommit){
      if(pr){
        sendSelectedPr([pr,selectedCommit]);
        return;
        //fetchPullResult(pr, selectedCommit);
      }
      else if(selectedPr){
        sendSelectedPr([selectedPr,selectedCommit]);
        return;
        //fetchPullResult(selectedPr, selectedCommit);
      }
    }
    sendSelectedPr(false);
  };

  const prList = [<option value={0} key={0}>Compare Pull Request...</option>];
  for (var pr of prs){
    prList.push(<option value={pr} key={pr}>{pr}</option>);
  }

  return <>{prs.length===0 ?
    "" :
    <>
    <span className="col-sm-4 col-md-4">
    <select id="prPicker" name="prPicker" className="form-select"
            onChange={(ev)=>prSelected(ev.target.value)} style={{display: "inline"}}>
    {prList}
    </select>
    </span>
    <span className="col-sm-4 col-md-4">
    <select id="commitPicker" name="commitPicker" className="form-select"
            onChange={(ev)=>{commitSelected(ev.target.value)}} style={{display:"none"}} disabled={true}>
    {commitList}
    </select>
    </span>
    </>
  }</>;


}
