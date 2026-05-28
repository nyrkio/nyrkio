import { Link } from "react-router-dom";

import gh_permissions_img from "../static/github_permissions.png";
import imgMenuOrg from "../static/menu-org.png";
import imgOrgSettings from "../static/org-settings.png";

export const DocsTeams = () => {
  return (
    <>
      <div className="container nyrkio-docs text-center">
      <Teams />
      </div>
    </>
  );
};


const Teams = () => {
  return (
    <>
      <div>
        <h1>Working with Teams / Orgs</h1>

        <p>The Team (or Orgs) support allows multiple persons from the same company, or just collaborators
        of the same github project, to work together on uploading test results to Nyrkiö, and getting alerts
        of regressions. At the moment Nyrkiö org support is tightly integrated with Github's team management.
        When you enable Nyrkiö GitHub app for a repo,
        or for the entire GitHub org, then all users who are
        members of that GitHub org will automatically also be members of the corresponding Nyrkiö team.</p>
        <p><b className="protip">Pro tip:</b> If you are using Nyrkiö for an open source project, that has many contributors
        that aren't and cannot be given write permission to the github repo in question, then your best bet is typically to
        make your test results public. And it is of course possible to use both the Orgs API and
        make those results public.</p>
        <p><b className="protip">Pro tip:</b> Many settings in Nyrkiö are global for a given user. So you are forced
        to use the same p-value and minimum threshold everywhhere. Each Org actually has its own settings. Sometimes
        you may want to use an Org for some test results just to enable a different configuration for that set of results.</p>

        <div className="d-flex flex-column flex-md-row gap-2 gap-md-4 justify-content-center mb-4 mb-md-6">
          <Link className="btn btn-primary" to="/public">Public Test Results</Link>
          <Link className="btn btn-outline-primary" to="https://github.com/apps/nyrkio/installations/new">Get started with GitHub</Link>
        </div>

        <h2>Using Nyrkiö with GitHub Orgs</h2>

        <p>To enable orgs support in Nyrkiö, start by going to GitHub apps installation
        page. Select the org or repo.</p>

        <img src={gh_permissions_img} className="p-3"/>


        <div className="mt-4 mb-5">
          <Link className="btn btn-outline-primary" to="https://github.com/apps/nyrkio/installations/new">Get started with GitHub</Link>
        </div>

        <div className="row my-4">
          <div className="col-md-6">
            <p>Once you return to Nyrkiö, the newly added org will be visible in the top right menu:</p>
            <img src={imgMenuOrg} width="400" height="469" alt="Screenshot of account menu"/>
          </div>
          <div className="col-md-6">
            <p>The org has its own settings page, and from that page you can also see the base URL that you should use to post benchmark results so that they are shared with the org:</p>
            <img src={imgOrgSettings} width="550" height="432" alt="Screenshot of settings" />
          </div>
        </div>

        <p>So in the above example, any test results posted at https://nyrkio.com/orgs/nyrkio are shared with everyone who is a member of the  <em>nyrkio</em> org in GitHub. For full API docs, see:</p>
        <Link className="btn btn-primary" to="https://nyrkio.com/openapi#/default/add_result_api_v0_orgs_result__test_name__post">API Docs</Link>

      </div>
    </>
  );
};

const DemoVideo = () => {
  return (
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
  );
};
