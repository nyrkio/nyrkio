import { useState, useRef, useEffect } from "react";
import { Button, Modal, ModalHeader } from "react-bootstrap";
import { Line } from "react-chartjs-2";
// DO NOT REMOVE
// necessary to avoid "category is not a registered scale" error.
import { Chart as ChartJS } from "chart.js/auto";
import { parseTimestamp } from "../lib/utils";

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
}) => {
  const chartRef = useRef();
  const metricName = metric["name"];
  const metricUnit = metric["unit"];
  const parseData = (data, metricName) => {
    const value_map = data.map(
      (result) =>
        result.metrics
          .filter((metric) => metric.name === metricName)
          .map((metric) => metric.value)[0],
    );
    return value_map;
  };

  // {'testName':
  //    [{
  //      'time': 123,
  //      'changes': [{'forward_change_percent': 900, 'metric': 'metric1'}]
  //    }]
  // }
  const changePointTimes = [];

  // TODO(mfleming) Assumes a single testName but must handle multiple
  // tests in the future.
  Object.entries(changePointData).forEach(([testName, value]) => {
    value.forEach((changePoint) => {
      const metrics = changePoint["changes"].map((change) => {
        return change["metric"];
      });
      console.log(metrics);
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

  const PopupModal = ({ show, setShow, timestamp, setTimestamp }) => {
    const handleClose = () => setShow(false);

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
      "nearest",
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

  const [showModal, setShowModal] = useState(false);
  const [modalData, setModalData] = useState({});
  return (
    <>
      <PopupModal
        show={showModal}
        setShow={setShowModal}
        timestamp={modalData}
        setTimestamp={setModalData}
      />
      <div className="chart-wrapper p-4">
        <h6 className="text-center">
          {testName}: {metricName}
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
                data: parseData(displayData, metricName),
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
            },
            hover: {
              mode: "nearest",
              intersect: false,
            },
            plugins: {
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
                    var labelArray = ["value: " + context.raw + metricUnit];

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
          }}
        />
      </div>
    </>
  );
};
