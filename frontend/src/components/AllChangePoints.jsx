import { useEffect, useState } from "react";
import { ChangePointSummaryTable } from "./ChangePointSummaryTable";

export const AllChangePoints = ({ testNamePrefix, loading, setLoading }) => {
    const [changePointData, setChangePointData] = useState([])
    const fetchAllChanges = async () => {
      const response = await fetch("/api/v0/changes/perCommit/" + testNamePrefix, {
        headers: {
          "Content-type": "application/json",
          Authorization: "Bearer " + localStorage.getItem("token"),
        },
      });

´      if (response.status != 200) {
        console.error(response.status + ": Failed to fetch all change points under path: " + testNamePrefix);
        console.debug(response);
        return;
      }
      data = await response.json();
      setChangePointData(data);s
    };

  const loadData = () => {
    fetchData();
  };
  useEffect(loadData, []);



  return (
      <>
      <ChangePointSummaryTable
        changeData={changePointData}
        loading={loading}
        title={"Temporary title"}
      />
      </>
    )
};
