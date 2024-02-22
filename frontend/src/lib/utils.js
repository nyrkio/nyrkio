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
export const throttle = function( fn, delay ) {
    var timer = null;
    return function() {
        var context = this, args = arguments;
        window.clearTimeout( timer );
        timer = window.setTimeout( function() {
            fn();
            //fn.apply( context, args );
        }, delay );
    };
};
