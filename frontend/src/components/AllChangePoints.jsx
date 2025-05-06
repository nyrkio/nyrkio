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
//       console.debug(changePoint);
//       const changes = changePoint["changes"];
//       console.debug(changes);
//       changes.map((change) => {
//         const commit = changePoint["attributes"]["git_commit"];
//
//         let commit_msg = "";
//         if (changePoint["attributes"].hasOwnProperty("commit_msg")) {
//           commit_msg = changePoint["attributes"]["commit_msg"];
//         }
//
//         const repo = changePoint["attributes"]["git_repo"];
//         const changeValue = change["forward_change_percent"];
//         const metric_name = change["metric"];
//         rowData.push({
//           date: parseTimestamp(changePoint["time"]),
//           commit: { commit, commit_msg, repo },
//           metric: metric_name,
//           change: { changeValue, metric_name }
//         });
//       });
//     });
//   });
//

// branch
// :
// "master"
// change_points_timestamp
// :
// "2025-01-02T00:25:02.305000"
// commit_timestamp
// :
// 1694449670
// repo
// :
// "https://github.com/facebook/rocksdb"
// _id
// :
// commit
// :
// "ed5b6c0d99f7cba6ac4c49c2ace8ea094f3884ba"
// max_pvalue
// :
// 0.001
// min_magnitude
// :
// 0.05
// user_id
// :
// 5477410


      const data = await response.json();

      const wrapper = {};
      wrapper[testNamePfx] = data;
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
