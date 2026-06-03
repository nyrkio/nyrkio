import { Link } from "react-router-dom";

import imgSettingsSlack from "../static/docs/settings-slack.png";
import imgUiFrontpage from "../static/docs/ui-frontpage.png";
import imgUiResult2 from "../static/docs/ui-result2.png";
import imgUiResultHover from "../static/docs/ui-result-hover.png";
import imgUiResultModal from "../static/docs/ui-result-modal.png";
import imgUiResult from "../static/docs/ui-result.png";
import imgUiResultAll from "../static/docs/ui-result-all.png";
import imgUiSettingsLayout from "../static/docs/ui-settings-layout.png";
import imgUiSettingsParams from "../static/docs/ui-settings-params.png";
import imgUiSettingsPublic from "../static/docs/ui-settings-public.png";
import '../style/components/nyrkio-docs.scss';


export const DocsGraphs = () => {
  return (
    <div className="container text-center nyrkio-docs">
      <Graphs />
    </div>
  );
};


const Graphs = () => {
  return (
    <>
      <div>
        <h1>Working with the Nyrkiö UI and Graphs</h1>

        <p>Once you have uploaded some of your benchmark results you can head to <Link to="https://nyrkio.com">nyrkio.com</Link>, make sure you are logged in, and start analyzing your results.</p>
        <div className="d-flex flex-column flex-md-row gap-2 gap-md-4 justify-content-center mb-4 mb-md-6">
          <Link className="btn btn-primary" to="/login">logged in</Link>
          <Link className="btn btn-outline-primary" to="/docs/getting-started">Nyrkio Runners</Link>
        </div>

        <DemoVideo />

        <p><b className="protip text-secondary">Pro tip:</b> The Nyrkiö User interface is a React frontend that operates
            against the Nyrkiö APIs. The API exposes more functionality than what is available in the UI. Please
            consult the API documentation for using the full functionality.</p>
        <p><b className="protip text-secondary">Pro tip:</b> <Link to="https://github.com/nyrkio/nyrkio">Nyrkiö is 100% open source software</Link>,
           including the User Interface. You can
           fork and run your own version of the frontend directly against the official nyrkio.com backend.</p>
        <Link className="btn btn-primary mb-4 mb-md-6" to="/openapi">API Docs</Link>


        <h2>Navigating the Graphs</h2>

        <p>Click on the top left Nyrkiö logo to get to the starting page. Here you will see a listing of the benchmark
           results that were successfully uploaded. For example, if you followed the getting
           started example, you will see "benchmark1" here. You will also see a copy of the tigerbeetle dataset, which
           we copy to all new user accounts so you have some data to watch even if you didn't yet run your own benchmarks.</p>
        <div>
          <Link className="btn btn-outline-primary mb-4 mb-md-6" to="/docs/getting-started">Nyrkio Runners</Link>
        </div>


        <img src={imgUiFrontpage} alt="Screenshot of UI select" width="700" height="518" className="mb-4"/>

        <p>Select one of the links from the list. If you used slashes ( this: / ) in the URI when you uploaded the results,
          Nyrkiö will break your test name into parts and display your uploaded results as a hierarchy. Very much like folders
          on your computer.</p>

        <p>The testname, with slashes if you used any, is shown on the top of each page to help you navigate. You can also click on
           each part to step back up in the hierarchy.</p>

        <img className="mb-4" width="700" height="608" src={imgUiResult} alt="Screenshot of perfomance test results" />

        <p>If Nyrkiö found some change points in your benchmark results, they will be listed in the table on top.
           You can click on the metric (second column) and you will jump directly to the graph where that change point was found.</p>

        <p>If you click on the git commit message in the right most column, you'll be taken to github to that very commit. Once you know
           which commit caused a regression, it's usually a straightforward excercise to figure out why that patch made your software slower.
           Or faster! Nyrkiö will alert you for changes in both directions!</p>

        <img className="mb-4" src={imgUiResult2} width="700" height="651" alt="Screenshot of metrics"/>

        <p>Each graph is zoomable. Select a range to zoom in. After zooming you can pan the range left and right. To zoom again you first
           have to click on "Reset zoom".</p>

        <p>For performance reasons, the number of points is currently limited at 300.</p>

        <p>Note that the number of points you can store may also be limited by your subscription level.</p>

        <Link to="/pricing" className="btn btn-outline-primary">Pricing</Link>
        <hr className="mb-4 mb-md-6"/>

        <h2>Viewing data about each point</h2>
        <p> If you hover over each data point, you can view some data about each point. A change point will also show
            the change in percentage, pvalue and other statistics.<br />The lower the pvalue, the more certain the algorithm was about
            flagging this change point.</p>

        <img className="mb-4" src={imgUiResultHover} width="700" height="651" alt="Screenshot of metrics on hover"/>

        <p>To view all of the information attached to each point, click on a point and use the Next and Previous buttons to navigate:</p>

        <p><span className="protip">Pro tip:</span> The <code className="badge text-bg-secondary">extra_info:</code> key allows you to attach any additional information you want to your payload.
        This can be useful to add more context for debugging purposes.</p>

        <img className="mb-4" src={imgUiResultModal} width="700" height="651" alt="Screenshot of modal result" />

        <p>If you have a deep hierarcy of results, you will eventually see a button on your bottom right labeled "Show graphs here". This allows you to
           view all remaining graphs as a flat list on the same page. <br/>At most 30 graphs can be shown on a single page.</p>

        <img width="700" height="571" src={imgUiResultAll} alt="Screenshot of graphs" />
        <hr/>
        <h2>Configuration</h2>

        <p className="mb-4">Click on the gear to your right to open up a configuration panel.</p>

        <h3>Page layout</h3>
        <img width="700" height="486" src={imgUiSettingsLayout} alt="Srenshot of layout settings" className="mb-4"/>

        <p>In the first section you can select different ways to layout the graphs on a page.</p>

        <p>Select the first two layouts to fit many graphs on the same screen. This will give you a quick overview.</p>

        <p>Select the layouts with larger graphs to analyze in detail and accentuate small ups and downs in the data.</p>

        <p>The embed layout is designed to be used as an iframe in your own dashboards. It will remove menus and other unnecessary components to highlight just the data itself.</p>

        <p>The selected layout will be used on each page for the same browser. If you use a different browser or device, each will remember their own layout.</p>

        <h3 className="mt-4 mt-md-6">Change Detection Sensitivity</h3>

        <p>The change detection algorithm can be tweaked with two parameters. The main parameter is the p-value. It sets the required threshold for <em>statistical significance</em> when Nyrkiö decides to flag a change point. In a way, the p-value is the probability of false positives. For example, using a p-value of <em>0.01</em> you would expect to get a false positive for every 99 real regressions (or improvements). In practice things aren't exactly like that.</p>

        <p>The Change magnitude can be used to simply discard all change points that are smaller than this threshold. For example, you might not care about a 1% regression
           even if it is statistically significant and "real".</p>

       <p>Different Nyrkiö users have different preferences for how sensitive they want the detection to be. Some users don't want to be constantly alerted by small performance
          variations, they only want to know if something really bad happened. For this, set the p-value to a really small value and the change magnitude as high as you want to ignore
          smaller changes. For example [p-value=0.001 and magnitude=5%].</p>

      <p>If performance is really important to you, and you want to be alerted for absolutely every performance change, and will tolerate some false positives, set the magnitude
      to 0% or 0.5% and the p-value to a modestly low value like 0.01 or 0.05.</p>

        <img src={imgUiSettingsParams} width="700" height="638" className="mb-4" alt="Screenshot of graph settings"/>

        <p>Note that these parameters are global and will cause all of your change points to be recomputed for all your benchmark results.</p>

        <p><span className="protip">Pro tip</span>: The Business and Enterprise plans include support for teams. Each team can have different configuration for change detection sensitivity.</p>
        <Link to="/pricing" className="btn btn-outline-primary mb-4 mb-md-6">Pricing</Link>

        <h3>Making your results public</h3>

        <p>The last configuration option allows you to publish your benchmark results and the change points found. Many users find this convenient as they don't need to
        be logged in to Nyrkiö at all to check their latest performance results. This is particularly useful for open source projects that prefer project information to
        be publicly available anyway.</p>

        <img src={imgUiSettingsPublic} width="700" height="186" alt="Screenshot of public option setting" className="mb-2" />

        <p>This setting is separate for each page.</p>

        <hr/>

        <h2>Alerts</h2>

        <p>To configure slack alerts, click on the user menu on your top right, and select User Settings. Scroll down until you see "Slack".</p>
        <img src={imgSettingsSlack} width="700" height="269" className="mb-4" alt="Screenshot of slack settings"/>

        <p>Click on the button, give Nyrkiö permission to access your Slack workspace, select the channel where you want alerts to go, and you're set!</p>

        <p>Note that Nyrkiö also supports commenting on PRs, but this is not available in the UI. Please use the <Link to="/openapi">API</Link> to enable Github integration.</p>

        <p>For paid subscriptions, we also support email and Jira integration. (Contact us for details.)</p>
        <Link className="btn btn-outline-primary" to="/pricing">Pricing</Link>
        <hr/>

        {
// import imgSettingsSlack from "../static/docs/settings-slack.png";
// import imgSettingsUserInfo from "../static/docs/settings-userinfo.png";
//
//         url: to graph, to anchor, to commit
//         notifications
        }
      </div>
    </>
  );
};

const DemoVideo = () => {
  return (
    <div className="ratio ratio-16x9 mx-auto my-5 my-md-6" style={{maxWidth: "860px"}}>
      <iframe
        width="560"
        height="315"
        src="https://www.youtube.com/embed/OmzcWan-Rew?si=D1g49njB98kyoU1k"
        title="YouTube video player"
        frameBorder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        referrerPolicy="strict-origin-when-cross-origin"
        allowFullScreen
      ></iframe>
    </div>
  );
};
