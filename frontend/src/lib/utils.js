import { format } from "date-fns";

export const parseTimestamp = (t) => {
  const utcSeconds = t;
  var d = new Date(0);
  d.setUTCSeconds(utcSeconds);
  return format(d, "yyyy-MM-dd HH:mm");
};

export const formatCommit = (commit, commit_msg) => {
  // Limit the git commit sha to 12 characters to improve readability
  var commitString = commit.substring(0, 12);
  if (commit_msg !== "") {
    commitString += ' ("' + commit_msg + '")';
  }
  return commitString;
};

// Throttling function calls, by Remy Sharp (via impress.js...)
// http://remysharp.com/2010/07/21/throttling-function-calls/
export const throttle = function (fn, delay) {
  var timer = null;
  return function () {
    var context = this,
      args = arguments;
    window.clearTimeout(timer);
    timer = window.setTimeout(function () {
      fn();
      //fn.apply( context, args );
    }, delay);
  };
};

// Build a URL from a test result' attributes and test name.
// If we're accidentally passed a string that isn't a GitHub URL, just
// return the original string.
export const parseGitHubRepo = (result) => {
  const url = result.attributes.git_repo;
  if (!url.startsWith("https://github.com/")) return url;

  // const path = url.replace("https://github.com/", "");
  // url encode url
  const path = encodeURIComponent(url);
  return path + "/" + result.attributes.branch + "/" + result.test_name;
};

// Convert an array of testnames, potentially with "/" separators, into an array
// of short names.
//
// A short name is the first part of a test name, up to the first "/", e.g.
// "foo/bar/baz" -> "foo".
//
// This function is used by the dashboard code (PublicDashboard and Dashboard).
export const createShortNames = (prefix, testNames) => {
  var shortNames = [];
  if (prefix === undefined) {
    shortNames = testNames
      .map((name) => name.split("/")[0])
      .filter((v, i, a) => a.indexOf(v) === i);
  } else {
    // remove prefix from name
    shortNames = testNames
      .filter((name) => {
        // Prefix must be an exact match
        return (
          name.startsWith(prefix) &&
          name.length > prefix.length &&
          name.substring(prefix.length, prefix.length + 1) === "/"
        );
      })
      .map((name) => {
        var shortName = name.replace(prefix + "/", "");
        return shortName.split("/")[0];
      })
      .filter((v, i, a) => a.indexOf(v) === i);
  }
  return shortNames;
};

// We have multiple kinds of dashboards, each with some different behavior.
//
// Organization dashboards are for viewing the results of tests that belong to
// an organization. User dashboards are for viewing the results of tests that
// belong to a single user. And finally public dashboards are for viewing the
// results of tests that have been shared publicly.
//
// Both org and user dashboards have the ability to toggle test visibility, i.e.
// make a test public or private. Public dashboards do not have this ability and
// are basically read-only.
//
// Crucially, the API endpoints used to toggle test visibilty are different for
// each kind of dashboard. This is why we need to know what kind of dashboard we're
// dealing with.
export const dashboardTypes = {
  ORG: "org",
  PUBLIC: "public",
  USER: "user",
};
