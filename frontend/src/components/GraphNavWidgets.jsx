export const GraphNavWidgets = ({
    firstGraphIndex,
    setFirstGraphIndex,
    maxGraphsPerPage,
    numGraphs,
}) => {


    const Previous = ({ firstGraphIndex, setFirstGraphIndex,total,  maxGraphsPerPage }) => {
        const under = firstGraphIndex;
        return (
            <button className="graph-nav btn btn-primary"
            title="Show more graphs" type="button" id="previousGraphsButton" data-bs-toggle="collapse"
            onClick={(ev)=>{setFirstGraphIndex( Math.max(0, firstGraphIndex-maxGraphsPerPage/2))}}
            >
            {under} previous graphs ⮝
            </button>
        );
    };

    const More = ({ firstGraphIndex, setFirstGraphIndex, total, maxGraphsPerPage }) => {
        const over = Math.max(total-firstGraphIndex-maxGraphsPerPage, 0);
        return (
            <button className="graph-nav btn btn-primary"
            title="Show more graphs" type="button" id="previousGraphsButton" data-bs-toggle="collapse"
            onClick={(ev)=>{setFirstGraphIndex( Math.min(total-maxGraphsPerPage, firstGraphIndex+maxGraphsPerPage/2))}}
            >
            {over} more graphs ⮟
            </button>
        );
    };

    let moreVis = 0;
    let prevVis = 0;
    if(            numGraphs-maxGraphsPerPage-firstGraphIndex>0) {
        moreVis = 1;
        prevVis = 0.3;
    }
    if( firstGraphIndex>0) {
        moreVis = moreVis?moreVis:0.3;
        prevVis = 1;
    }
    return (
        <>
        <div className="row graphNavWidgets">
        <span className="col-sm-1 col-md-1 col-lg-1"></span>
        <span className="col-sm-4 col-md-4" style={{"opacity": moreVis}}>
            <More firstGraphIndex={firstGraphIndex}  total={numGraphs} setFirstGraphIndex={setFirstGraphIndex} maxGraphsPerPage={maxGraphsPerPage} />
        </span>
        <span className="col-sm-4 col-md-4" style={{"opacity": prevVis}}>
            <Previous firstGraphIndex={firstGraphIndex} total={numGraphs} setFirstGraphIndex={setFirstGraphIndex} maxGraphsPerPage={maxGraphsPerPage} />
        </span>
        <div className="col-sm-3 col-md-3 col-lg-3">&nbsp;
        </div>
        </div>
        </>
    );


};

