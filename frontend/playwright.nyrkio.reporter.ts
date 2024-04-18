import type {
  FullConfig, FullResult, Reporter, Suite, TestCase, TestResult
} from 'playwright/test/reporter';

import gitCommitInfo from 'git-commit-info';
import branchName from 'current-git-branch';

class NyrkioTestResult {
  private doc: Object;
  private path: Array;

  constructor(
    gitRepo: string,
  ){
    this.path=new Array();
    var ts = (new Date(gitCommitInfo().date))/1000.0;
    this.doc = {
      "timestamp": ts, // This is wrong we need the merge commit date really
      "metrics": [],
      "attributes": {
        "git_repo": undefined, // From config
        "branch": branchName(),
        "git_commit": gitCommitInfo().commit,
      }
    };


    this.doc.attributes.git_repo = gitRepo;
  }

  private metricTemplate (){
      return {"name": undefined, "unit": "s", "value": undefined };

  }

  public addMetric(name:string, unit: string, value: Number){
    var m = this.metricTemplate();
    m.name = name;
    m.unit = unit;
    m.value = value;
    this.doc.metrics.push(m);
  }

  public getPath( ){
    return this.path.join("/");
  }
  public pathPrefix( name:string){
    if(name.slice(0,6)=="tests/") {
      name = name.slice(6); // Remove redundant top directory
    }
    this.path.unshift(name);
  }

  public toJSON(){
    return JSON.stringify(this.doc);
  }

  public getResult (){
    return this.doc;
  }
}


class NyrkioReporter implements Reporter {
  private results: Array;
  private gitRepo: string;
  private projectName: string;

  constructor(options: {}){
    this.gitRepo = options.gitRepo;
    this.projectName = options.projectName;
    this.results = new Array();
  }

  onTestEnd(test: TestCase, result: TestResult) {
    var nyrkioResult = new NyrkioTestResult(this.gitRepo);
    nyrkioResult.pathPrefix(test.title);
    var parent = test.parent;
    while(parent.title != "" && parent.type!="root"){
      nyrkioResult.pathPrefix(parent.title);
      parent = parent.parent;
    }
    nyrkioResult.pathPrefix(branchName());
    nyrkioResult.pathPrefix(this.projectName);

    nyrkioResult.addMetric ("test duration", "msec", result.duration);
    this.results.push (nyrkioResult);
  }

  async onEnd(result: FullResult) {
    //console.log(this.results);
    //console.log(this.results[0]);
    console.log("posting results to nyrkio.com");
    for(var r of this.results){
      await this.post(r);
    }
  }

  private async post(nyrkioResult){
    const url = "https://nyrkio.com/api/v0/result/" + nyrkioResult.getPath();
    const body = JSON.stringify([nyrkioResult.getResult()]);
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + process.env.NYRKIO_TOKEN,
      },
      body: body,
    });
    if (response.status !== 200) {
      console.error("Failed to POST results to Nyrkiö API: " + url);
      console.log(body);
      console.log(response);
      return false;
    } else {
      //console.debug(response);
      console.log("Test durations were posted to Nyrkiö. View them at https://nyrkio.com/tests/"
                  + this.projectName + "/" +branchName());
      return true;
    }
  }
}

export default NyrkioReporter;
