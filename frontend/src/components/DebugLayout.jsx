import { useState, useEffect } from "react";


const groupCSS = (which) => {
    let groups = {};
    let comp = getComputedStyle(document.documentElement);
    let w;
    Object.entries(comp).map((k,v)=> {
        w = comp[v];
        if (w === undefined)return "";

        let group = w.split("-")[0];
        if (! groups[group] ){
            groups[group] = []
        }
        groups[group].push(v);
    });
    const cssGroups = [];
    const cssOther = [];
    Object.entries(groups).map((k,v) => {
        if (k[1].length > 1 ) {
            cssGroups.push(k[0]);
        }
        else {
            cssOther.push(comp[k[1][0]]);
        }

    });
    return {cssGroups, cssOther};
};
const CSSGroups = ({groups, setState}) => {
    const cssGroups = [];
    groups = groups || [""];
    for (let o of groups){
        if (o==""){
            cssGroups.push(<a key={"other"} href="#" onClick={() => openGroup("other", setState)}>other</a>);
            continue;
        }
        const a = (<a key={o} href="#" onClick={() => openGroup(o, setState)}>{o}</a>)
        cssGroups.push(a);
        cssGroups.push(" | ")
    }

    return cssGroups;
};


const openGroup = (g, setState) => {
    setState(g);
}

const DebugLayoutRow = ({group, cssGroups, other, element}) => {
    let comp = getComputedStyle(element);
    if (group=="other"){
        return    (<>{other.map((k,v)=> {
            return (<tr key={v}><td>{k}</td><td>{comp[k]}</td></tr>);
        })}</>);
    }

    return    (<>{Object.entries(comp).map((k,v)=> {
        if (comp[v] === undefined) return;
        const w = comp[v];
        let rowInGroup = w.split("-")[0];
        if (rowInGroup==group){
            return (<tr key={v}><td>{comp[v]}</td><td>{comp[comp[v]]}</td></tr>);
        }


    })}</>);

};


export const DebugLayout = () =>{
    if(localStorage.getItem("username")!="henrik@nyrk.io"){
        return "";
    }
    const [queryString, setQueryString] = useState();
    const [cssGroups2, setCssGroups2] = useState([])
    const [cssOther2, setCssOther2] = useState([])
    const [openCssGroup, setOpenCssGroup] = useState([]);

    const debugElementCss = (e) => {
        const qs = e.target.previousSibling.value;
        setQueryString(qs)  ;
        const {cssGroups, cssOther} = groupCSS();
        setCssGroups2(cssGroups);
        setCssOther2(cssOther);
        setOpenCssGroup(cssGroups?cssGroups[0]:[]);

    };
    let element="";
    if(queryString){

        element = document.querySelector(queryString);
        if(element)
            element.style.border = "1px red solid";
        else
            element = document.documentElement;
    }


  return (<>
    <div className="debug-info">
        <hr className="mt-5 mb-5" />
        <table>
        <thead>
            <tr>
                <th colSpan="2"><input type="text" name="debugCssQueryString" placeholder="body" /><button type="submit" onClick={debugElementCss}>Show Computed CSS</button></th>
            </tr>
        </thead>
        {queryString && element? (
        <tbody>
            <tr>
                <td>Page Width x Height</td>
                <td>{window.innerWidth} x {window.innerHeight}</td>
            </tr>
            <tr>
                <td>{element.tagName} Width x Height</td>
                <td>{element.innerWidth} x {element.innerHeight}</td>
            </tr>
            <tr>
            <td colSpan={2}>
            <CSSGroups groups={cssGroups2} setState={setOpenCssGroup}/>
            </td>
            </tr>
            <DebugLayoutRow group={openCssGroup} cssGroups={cssGroups2} other={cssOther2} element={element}/>
        </tbody>)
        : "" }
        </table>
    </div>
    </>);
};

