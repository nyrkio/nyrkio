import { useEffect, useState } from "react";
import { ChangePointSummaryTableMain } from "./ChangePointSummaryTableMain";
import { useLocation } from "react-router-dom";
import { useSearchParams } from "react-router-dom";

export const AllChangePoints = ({ testNamePrefix, baseUrls }) => {
    const [searchParams, setSearchParams] = useSearchParams();
    if(!searchParams.has("preview")){
      return (<><div className="row justify-content-center"></div></>);
    }
    const location = useLocation();
    if(testNamePrefix===undefined) testNamePrefix="/";

    if ( baseUrls.apiRoot.endsWith("public/") && testNamePrefix=="/") return (<></>);
    if ( baseUrls.apiRoot.endsWith("orgs/") && testNamePrefix=="/") return (<></>);

    const [changePointData, setChangePointData] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchAllChanges = async (testNamePfx) => {
      let url = baseUrls.apiRoot + "changes/perCommit/" + testNamePfx;
      if (testNamePfx!=="" && testNamePfx.substring(0,1) == "/" ) {
        url = baseUrls.apiRoot + "changes/perCommit" + testNamePfx;
      }

      const response = await fetch(url, {
        headers: {
          "Content-type": "application/json",
          Authorization: "Bearer " + localStorage.getItem("token"),
        },
      });

      if (response.status != 200) {
        console.error(response.status + ": Failed to fetch all change points under path: " + testNamePrefix);
        console.debug(response);
        return false;
      }

      const data = await response.json();

      const wrapper = {};
      wrapper[testNamePfx] = data;
      setChangePointData(wrapper);
      return true;
    };

  const loadData = () => {
    console.log("testNamePrefix: " + testNamePrefix);
    if(testNamePrefix!==undefined){
      setChangePointData({});
      setLoading(true);
      fetchAllChanges(testNamePrefix).then((result)=> {if(result){setLoading(false); console.log("loading false");}});

    }
  };
  useEffect(loadData, [location]);



  return (
      <>
      <div className="row justify-content-center">
      <ChangePointSummaryTableMain
        changeData={changePointData}
        loading={loading}
        baseUrls={baseUrls}
      />
      </div>
      </>
    )
};
