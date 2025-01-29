import { useState, useRef, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { Button, Modal, ModalHeader } from "react-bootstrap";
import { Line } from "react-chartjs-2";
import { Tooltip } from "chart.js";
// DO NOT REMOVE
// necessary to avoid "category is not a registered scale" error.
import { Chart as ChartJS } from "chart.js/auto";
import zoomPlugin from 'chartjs-plugin-zoom';
import { parseTimestamp } from "../lib/utils";
ChartJS.register(zoomPlugin);

const nyrkio_dark_red = "#a34111";
const nyrkio_bright_red = "#dc3d06";
const nyrkio_tattoo_red = "#973212";
const nyrkio_dark_gray = "#a99883";
const nyrkio_light_gray = "#d1c1a8";
const nyrkio_light_gray2 = "#f1e8d8";
const nyrkio_light_gray3 = "#fff6e6";
const nyrkio_light_gray4 = "#fff9f1";
const nyrkio_light_gray5 = "#fffdf9";

const nyrkio_bear_brown = "#351406";
const nyrkio_horn_dark_brown = "#50320d";
const nyrkio_arrow_brown = "#7c5a32";
const nyrkio_horn_light_brown = "#b28b56";
const nyrkio_skin_light_brown = "#d2a376";

const nyrkio_text = "#344767";
const nyrkio_text_light = "#6c757d";

const nyrkio_chart_line_color = nyrkio_horn_light_brown;
const nyrkio_chart_cp_color = nyrkio_tattoo_red;

export const DrawLineChart = ({
  metric,
  testName,
  timestamps,
  displayData,
  changePointData,
  searchParams,
  graphSize
}) => {
  const chartRef = useRef();
  const metricName = metric["name"];
  const metricNameWithHash = "#"+metricName;
  const metricUnit = metric["unit"];
  let direction="";
  if (metric.direction=="higher_is_better") direction="Higher is better";
  if (metric.direction=="lower_is_better") direction="Lower is better";
  let directionArrow="";
  if (metric.direction=="higher_is_better") directionArrow=" ⇧";
  if (metric.direction=="lower_is_better") directionArrow=" ⇩";
  let metricAndDirection = metricUnit;
  if (metric.direction=="higher_is_better") metricAndDirection = metricUnit + " >";
  if (metric.direction=="lower_is_better") metricAndDirection = "< " + metricUnit;
  const parseData = (data, metricName) => {
    const value_map = data.map(
      (result) =>
        result.metrics
          .filter((metric) => metric.name === metricName)
          .map((metric) => metric.value)[0],
    );
    return value_map;
  };
  const getLayout = (layout) => {
    if(layout=="overview") return {width:"100%", maxWidth: "100%", outerWidth: "25%", height:"50%", maxHeight:"50%"};
    if(layout=="sparklines") return {width:"100%", height:"50px", maxHeight:"50px"};
    if(layout=="2x1") return {width: "100%", minWidth: "100%", height: "70%", maxHeight: "70%"};
    if(layout=="1x1") return {width: "100%", height: "90%", maxHeight: "90%"};
    return {width: "100%", height: "80%", maxHeight: "80%"};
  };
  const layout = getLayout(graphSize);

  const changePointTimes = [];

  // TODO(mfleming) Assumes a single testName but must handle multiple
  // tests in the future.
  Object.entries(changePointData).forEach(([testName, value]) => {
    value.forEach((changePoint) => {
      const metrics = changePoint["changes"].map((change) => {
        return change["metric"];
      });
//       console.debug(metrics);
      const t = changePoint["time"];
      changePointTimes.push({ t, metrics });
    });
  });

  var changePointIndexes = [];
  timestamps.map((timestamp, index) => {
    changePointTimes.map((change) => {
      const { t, metrics } = change;
      if (t !== timestamp) {
        return;
      }
      changePointIndexes.push({ index, metrics });
    });
  });
  function arrayMin(arr) {
    return arr.reduce(function (p, v) {
      return ( p < v ? p : v );
    });
  }

  function arrayMax(arr) {
    return arr.reduce(function (p, v) {
      return ( p > v ? p : v );
    });
  }
  function arrayMedian(arr) {
    const sorted = arr.sort()
    return sorted[Math.floor(sorted.length/2)]
  }
  const numSize = (numbers) => {
    const num = arrayMin(numbers);
    if(num > 1000*1000*1000*1000) return "trillion";
    if(num > 1000*1000*1000) return "billion";
    if(num > 1000*1000) return "million";
    // if(num > 1000) return "thousand";
    return "";
  };
  const numfmt = (num, cutTo) => {
    if(cutTo == "trillion") return Math.round(num / (1000*1000*1000*1000));
    if(cutTo == "billion") return Math.round(num / (1000*1000*1000));
    if(cutTo == "million") return Math.round(num / (1000*1000));
    if(cutTo == "thousand") return Math.round(num / (1000));
    return num;
  };

  const isChangePoint = (index) => {
    return changePointIndexes.find((element) => {
      return element.metrics.includes(metricName) && element.index === index;
    });
  };

  const pointRadius = (index) => {
    if (isChangePoint(index)) {
      return 3;
    }

    // If we have a lot of data points, don't show the points because the
    // chart lines become way too busy.
    return timestamps.length > 100 ? 0 : 1;
  };

  var userClosed = false;
  const PopupModal = ({ metricName, show, setShow, timestamp, setTimestamp }) => {
    const handleClose = () => {setShow(false); userClosed=true;};
    if(qtimestamp && showModal===null && !userClosed){
      //console.log(timestamps);
      console.log(timestamps.indexOf(qtimestamp));
      console.log(window.location.hash);
      if(timestamps.indexOf(qtimestamp)>=0 &&
        window.location.hash == "#"+metricName
      ){
        const e = document.getElementById(window.location.hash);
        if(e){e.scrollIntoView();}
        setModalData(parseTimestamp(qtimestamp));
        setShowModal(true);

      }
    }

    var result = displayData.find(
      (o) => parseTimestamp(o.timestamp) === timestamp,
    );

    if (result === undefined) {
      return <></>;
    }

    const result_index = displayData.indexOf(result);
    const metric = result.metrics.find((metric) => metric.name === metricName);
    const unit = metric.unit;
    const value = metric.value;

    const gh_link =
      result.attributes.git_repo + "/commit/" + result.attributes.git_commit;

    return (
      <>
        <Modal
          size="lg"
          show={show}
          onHide={handleClose}
          centered
          animation={false}
        >
          <Modal.Header closeButton>
            <Modal.Title>Test Result Data: {timestamp}</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <ul>
              <li>
                <b>value:</b> {value} {unit}
              </li>
              <li>
                <b>git repo: </b>
                {result.attributes.git_repo}
              </li>
              <li>
                <b>branch:</b> {result.attributes.branch}
              </li>
              <li>
                <b>git commit:</b>{" "}
                <a href={gh_link} target="_blank">
                  {result.attributes.git_commit}
                </a>
              </li>
              <li>
                <b>extra_info:</b>
                <pre>{JSON.stringify(result.extra_info, null, 2)}</pre>
              </li>
            </ul>
          </Modal.Body>
          <Modal.Footer>
            <Button
              variant="secondary"
              onClick={() => {
                if (result_index === 0) {
                  return;
                }
                const prev_timestamp = timestamps[result_index - 1];
                setTimestamp(parseTimestamp(prev_timestamp));
              }}
            >
              Prev
            </Button>
            <Button
              variant="secondary"
              onClick={() => {
                if (result_index === timestamps.length - 1) {
                  return;
                }
                const next_timestamp = timestamps[result_index + 1];
                setTimestamp(parseTimestamp(next_timestamp));
              }}
            >
              Next
            </Button>
          </Modal.Footer>
        </Modal>
      </>
    );
  };

  const chartClick = (e) => {
    const chart = chartRef.current;
    const points = chart.getElementsAtEventForMode(
      e.nativeEvent,
      "point",
      { intersect: false },
      true,
    );

    if (points.length === 0) {
      return;
    }

    const firstPoint = points[0];
    const label = chart.data.labels[firstPoint.index];

    setModalData(label);
    setShowModal(true);
  };

  const [showModal, setShowModal] = useState(null);
  const [modalData, setModalData] = useState({});
  const [queryParams, setQueryParams] = useSearchParams();
  const qtimestamp = parseInt(queryParams.get("timestamp"));
  useEffect(()=>{
  },[showModal, PopupModal]);

  const syncCharts = (target) => {
            const scaleX = target.chart.scales.x;
            const x = scaleX._range;
            const keys = Object.keys(ChartJS.instances);
            for (let i of keys){
              if(target.chart.id!=ChartJS.instances[i].id){
                ChartJS.instances[i].zoomScale('x',x, 'none');

              }
            }
        };
  const resetAllZooms = (ev) => {
    const buttons = document.getElementsByClassName("resetzoom");
    for (let b of buttons){
      b.style.opacity = 0;
    }
    // Will trigger syncCharts
    chartRef.current.resetZoom();
    const keys = Object.keys(ChartJS.instances);
    for (let i of keys){
      ChartJS.instances[i].zoom(1);
    }
  };
  const dontZoomAxes = ({chart, event, point}) => {
    console.debug(chart, event, point);
    console.debug(chart.getZoomLevel());
    if(chart.getZoomLevel() != 1){
      // You can zoom once, then you can pan
      console.log("Panning. Click 'Reset zoom' to zoom again.")
      return false;
    }
    const buttons = document.getElementsByClassName("resetzoom");
    for (let b of buttons){
      b.style.opacity = 0.5;
    }
    console.log("Zooming");
    return true;
  };
  const syncHover = (event, targets, chart) => {
//           if (targets && targets.length>0){
//             const dataset = targets[0].datasetIndex;
//             const idx = targets[0].index;
            if(chart.tooltip.title===undefined)
              return true; // first time, initialization isn't completed.

            if(event.type=="mousemove" || event.type=="mouseout"){
            const keys = Object.keys(ChartJS.instances);
            for (let i of keys){
              if(chart.id!=ChartJS.instances[i].id){
                 const  c = ChartJS.instances[i];
                 if(!c) continue;
                 if (!c.ctx) continue;
//                 console.log(c.tooltip);
                 c.tooltip.handleEvent(event,true,true);
                if(event.type=="mousemove"){
                  c.tooltip.opacity=1;
                  c.tooltip.active=true;

                }
                 c.tooltip.x = chart.tooltip.x;
                 for (let tipkey in chart.tooltip){
                   if(!c.tooltip[tipkey]){
                     c.tooltip[tipkey]=chart.tooltip[tipkey];
                  }
                }
                if(event.type=="mouseout"){
                  c.tooltip.opacity=0;
                  c.tooltip.active=false;

                }
                 const options = c.config._config.options.plugins.tooltip;
                 options.position="nearest";
                 c.tooltip._updateAnimationTarget(options);
                 c.draw(c.ctx);

                 c.tooltip.draw(c.ctx);
              }}
        }
        return true;
      };


        const dataValues = parseData(displayData, metricName);
        const numberSizeWord = numSize(dataValues);
        const cutValues = dataValues.map((v)=>numfmt(v, numberSizeWord));

        ChartJS.register({
           id: "mouseoutplugin",
           beforeEvent: function (chart, args, options){
             syncHover(args.event, null, chart);
           },
           beforeInit: function(){return true;},

        });
  return (
    <>
      <PopupModal
        metricName={metricName}
        show={showModal}
        setShow={setShowModal}
        timestamp={modalData}
        setTimestamp={setModalData}
      />
      <div className="outer-chart-wrapper" id={metricName} style={{maxWidth:layout.outerWidth}}>
      <div className="chart-wrapper"  style={layout}>
        <h6 className="text-center">
          <a href={metricNameWithHash}>{metricName}</a>{ " "}
          <span className="numfmt">{numberSizeWord?"("+numberSizeWord +")":""}</span>
          <span title={direction}>{directionArrow}</span>
        </h6>
        <Line
          ref={chartRef}
          datasetIdKey="foo"
          data={{
            labels: timestamps.map(parseTimestamp),
            datasets: [
              {
                id: 1,
                label: metricName,
                data: cutValues,
                fill: true,
                borderColor: nyrkio_chart_line_color,
                borderWidth: 2,
                maxBarThickness: 6,
                backgroundColor: ({ chart: { ctx } }) => {
                  const gradient = ctx.createLinearGradient(0, 230, 0, 50);
                  gradient.addColorStop(1, "rgba(209,193,168,0.2)");
                  gradient.addColorStop(0.2, "rgba(209,193,168,0.2)");
                  gradient.addColorStop(0, "rgba(255,249,241,0.3)");

                  return gradient;
                },
                pointBorderColor: (context) => {
                  return isChangePoint(context.dataIndex)
                    ? nyrkio_chart_cp_color
                    : nyrkio_chart_line_color;
                },
                pointBackgroundColor: (context) => {
                  return isChangePoint(context.dataIndex)
                    ? nyrkio_chart_cp_color
                    : nyrkio_chart_line_color;
                },
                pointRadius: (context) => {
                  return pointRadius(context.dataIndex);
                },
                pointHoverBorderColor: nyrkio_chart_line_color,
                pointHoverBackgroundColor: nyrkio_chart_line_color,
                pointHoverRadius: 3,
              },
            ],
          }}
          onClick={chartClick}
          options={{
            scales: {
              x: {
                grid: {
                  display: false,
                },
              },
              y: {
                title: {
                  display: true,
                  text: numberSizeWord + " " + metricAndDirection,
                }
              },
            },
            hover: {
              mode: "x",
              intersect: false,
            },
            onHover: syncHover,
            events: ['mousemove', 'mouseout', 'click', 'touchstart', 'touchmove', 'hover'],
            plugins: {
              mouseoutplugin: {opt:true},
              zoom: {
                zoom:{
                  wheel: {
                    enabled: false,
                  },
                  pinch: {
                    enabled: false
                  },
                  drag: {
                    enabled: true,
                    threshold: 10,

                  },
                  mode: 'x',
                  scaleMode: 'x',
                  onZoomComplete: syncCharts,
                  onZoomStart: dontZoomAxes,
                },
                pan: {
                  enabled: true,
                  mode: 'x',
                  scaleMode: 'x',
                  onPanComplete: syncCharts,
                  threshold: 100,
                },
                limits: {
                  x: {minRange: 10,}
                }
              },
              legend: {
                display: false,
              },
              interaction: {
                intersect: false,
                mode: "index",
              },
              tooltip: {
                displayColors: false,
                callbacks: {
                  label: (context) => {
                    var labelArray = ["value: " + context.raw + " " + metricUnit];

                    // Search in changePointData for this timestamp and metric
                    const timestamp = timestamps[context.dataIndex];
                    Object.entries(changePointData).forEach(
                      ([testName, value]) => {
                        value.forEach((changePoint) => {
                          if (changePoint["time"] === timestamp) {
                            labelArray.push("");

                            // Add all change point attributes to the label
                            changePoint["changes"].forEach((change) => {
                              if (change["metric"] !== metricName) {
                                return;
                              }

                              Object.entries(change).map(([key, value]) => {
                                if (key === "metric") {
                                  return;
                                }

                                var label = key + ": " + value;
                                if (key.includes("percent")) {
                                  label = label + "%";
                                }

                                labelArray.push(label);
                              });
                            });
                          }
                        });
                      },
                    );

                    return labelArray;
                  },
                },
                intersect: false,
              },
            },
            // Boolean - whether or not the chart should be responsive and resize when the browser does.
            responsive: true,
            // Boolean - whether to maintain the starting aspect ratio or not when responsive, if set to false, will take up entire container
            maintainAspectRatio: false,
          }}
        />
      </div>
      <button className="btn-secondary resetzoom" style={{opacity: 0}} onClick={(ev)=>resetAllZooms(ev)}>Reset zoom</button>
      </div>
    </>
  )};
