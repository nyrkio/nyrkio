import { useEffect, useState } from "react";
import { ChangePointSummaryTable } from "./ChangePointSummaryTable";

export const AllChangePoints = ({ testNamePrefix, baseUrls }) => {
    const [changePointData, setChangePointData] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchAllChanges = async (testNamePfx) => {
      const response = await fetch(baseUrls.apiRoot + "changes/perCommit/" + testNamePfx, {
        headers: {
          "Content-type": "application/json",
          Authorization: "Bearer " + localStorage.getItem("token"),
        },
      });

      if (response.status != 200) {
        console.error(response.status + ": Failed to fetch all change points under path: " + testNamePrefix);
        console.debug(response);
        return;
      }
      const data = await response.json();
      const wrapper = {};
      wrapper[testNamePfx]
      setChangePointData(wrapper);
    };

  const loadData = () => {
    if(testNamePrefix!==undefined){
      setLoading(true);
      fetchAllChanges(testNamePrefix).finally(()=> {setLoading(false); console.log("loading false");});

    }
  };
  useEffect(loadData, [testNamePrefix]);



  return (
      <>
      <div className="row justify-content-center">
      <ChangePointSummaryTable
        changeData={changePointData}
        loading={loading}
        title={"Temporary title"}
      />
      </div>
      </>
    )
};
