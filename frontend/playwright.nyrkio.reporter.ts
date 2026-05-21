import type {
  FullConfig,
  FullResult,
  Reporter,
  Suite,
  TestCase,
  TestResult,
} from "@playwright/test/reporter";

import gitCommitInfo from "git-commit-info";
import branchName from "current-git-branch";

const env = (globalThis as any).process?.env || {};

class NyrkioTestResult {
  private doc: any;
  private path: string[];

  constructor(gitRepo: string) {
    this.path = [];
    const ts = Date.now() / 1000.0;
    this.doc = {
      timestamp: ts, // This is wrong we need the merge commit date really
      metrics: [],
      attributes: {
        git_repo: undefined, // From config
        branch: branchName(),
        git_commit: gitCommitInfo().commit,
      },
    };

    this.doc.attributes.git_repo = gitRepo;
  }

  private metricTemplate() {
    return { name: undefined, unit: "s", value: undefined };
  }

  public addMetric(name: string, unit: string, value: Number) {
    var m: any = this.metricTemplate();
    m.name = name;
    m.unit = unit;
    m.value = value;
    this.doc.metrics.push(m);
  }

  public getPath() {
    return this.path.join("/");
  }
  public pathPrefix(name: string) {
    if (name.slice(0, 6) == "tests/") {
      name = name.slice(6); // Remove redundant top directory
    }
    this.path.unshift(name);
  }

  public toJSON() {
    return JSON.stringify(this.doc);
  }

  public getResult() {
    return this.doc;
  }
}

class NyrkioReporter implements Reporter {
  private results: any[];
  private gitRepo: string;
  private projectName: string;
  private enabled: boolean;
  private baseUrl: string;

  constructor(options: any) {
    this.gitRepo = options.gitRepo;
    this.projectName = options.projectName;
    this.results = [];
    this.enabled =
      env.NYRKIO_POST_RESULTS === "1" && !!env.NYRKIO_TOKEN;
    this.baseUrl = env.NYRKIO_BASE_URL || "https://nyrkio.com";
  }

  onTestEnd(test: TestCase, result: TestResult) {
    var nyrkioResult = new NyrkioTestResult(this.gitRepo);
    nyrkioResult.pathPrefix(test.title);
    let parent: any = test.parent;
    while (parent && parent.title != "" && parent.type != "root") {
      nyrkioResult.pathPrefix(parent.title);
      parent = parent.parent;
    }
    nyrkioResult.pathPrefix(branchName());
    nyrkioResult.pathPrefix(this.projectName);

    nyrkioResult.addMetric("test duration", "msec", result.duration);
    this.results.push(nyrkioResult);
  }

  async onEnd(result: FullResult) {
    //console.log(this.results);
    //console.log(this.results[0]);
    if (!this.enabled) {
      return;
    }
    console.log(`posting results to ${this.baseUrl}`);
    for (var r of this.results) {
      await this.post(r);
    }
  }

  private async post(nyrkioResult: any) {
    const url = `${this.baseUrl}/api/v0/result/${nyrkioResult.getPath()}`;
    const body = JSON.stringify([nyrkioResult.getResult()]);
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + env.NYRKIO_TOKEN,
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
      console.log(
        "Test durations were posted to Nyrkiö. View them at https://nyrkio.com/tests/" +
          this.projectName +
          "/" +
          branchName(),
      );
      return true;
    }
  }
}

export default NyrkioReporter;
