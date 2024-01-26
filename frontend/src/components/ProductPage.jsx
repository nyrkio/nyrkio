export const ProductPage = () => {
  return (
    <>
      <div className="container">
        <div className="row mt-8 p-5">
          <h1 className="font-weight-bolder text-center">
            Detecting performance regressions
          </h1>
          <h4 className="text-center">The hard way vs the smart way</h4>
        </div>
        <div className="row col-md-10 offset-md-1">
          <h3>Left shift performance</h3>
          <p>The word on the quality engineering streets is left shifting.</p>
          <p>
            Running automated unit and integration tests in Continuous
            Integration is nothing new. But on the performance testing front,
            it's been a slower shift. Automating large scale performance
            workloads so they can be scheduled automatically at night is both
            harder, but above all more expensive, than simple unit testing. Yet
            the days when performance testing mostly meant an annual rush to
            test the new release candidates are gone. Increasingly all serious
            software development teams do run nightly performance tests, and
            sometimes even before merging.
          </p>

          <p>
            And yet... Those that have gotten serious performance testing setup
            for continuous integration, will soon find out that running the test
            was just the beginning. Because once you got that far...
          </p>

          <p>What should you do with the results???</p>
        </div>
        <div className="row col-md-10 offset-md-1">
          <div className="col">
            <h3>The hard way</h3>
            <p>
              Unlike unit and other correctness tests, the result of a
              performance benchmark is not a simple pass or fail, wrong or
              correct. Benchmarking produces a number, or several, and the
              sequence of nightly builds produces a timeseries. But what should
              we do - and how should we automate - to analyze hundreds of
              nightly numeric values?
            </p>

            <p>
              The common approach is to simply continue what you have done
              before: The performance engineer will look at - yes, eyeballing -
              hundreds of metrics on half a dozen Grafana dashboards, and in
              their wisdom declare that performance <i>"looks good to me"</i>.
            </p>
          </div>

          <div className="col mt-4">
            <img
              style={{ height: "300px" }}
              src={"./src/static/Grafana_dashboard.png"}
            />
            <center>
              <a href="https://en.wikipedia.org/wiki/Grafana#/media/File:Grafana_dashboard.png">
                Image Credit: LinuxScreenshots @ Flickr
              </a>
            </center>
          </div>
        </div>
        <div className="row col-md-10 offset-md-1">
          <p>
            The naive way would then be to automate a simple{" "}
            <i>threshold based</i> comparison. If the result today is lower than
            last week, or yesterday, or the previous commit, should we consider
            the test as a failure?
          </p>

          <p>The answer is no.</p>

          <p>
            Performance results are a continuous metric. They are{" "}
            <i>better or worse</i>, not <i>pass or fail</i>. Two consecutive
            benchmarks will never produce the exact same result. The level of
            noise varies by application and test, but it is not unusual for a
            test to fluctuate between a 5-10% window. On the other hand some
            tests can be remarkably stable, so that anything above a 1% change
            stands out.
          </p>
        </div>
        <div className="row col-md-10 offset-md-1">
          <div className="col">
            <img src={"./src/static/50776727286_cdd63903f4_w.jpg"} />
            <center>
              <a href="https://www.flickr.com/photos/nenadstojkovic/50776727286/in/photolist-2kmXZZh-2mH2tsd-pNfG3r-9uaRmj-2m2cAtk-9o1FrD-2jJWW3T-2m4h9Tb-2joPwMv-p8adfb-pYmu5c-r5npnH-8jZGvy-pYrWxE-2m4GHWZ-CWBUK-pMyb4h-p89RRf-pYmd5g-2jJzX3w-pMY8PF-pYm1VH-2iocoyX-p8Eqfz-SRBJEv-p86duC-cp4eam-2joSi9a-8jZGjw-q5oEHM-q5n1fM-9GRwgf-5aMM2S-7Jw8UW-2UNrAs-6z4cGN-q5dA7i-p8CoLr-aLDiFR-4ZvDHZ-9anpxd-9STgSK-9dFg7Z-66XZaq-aYmSAK-2muF9rF-2kQVQ5M-4aCLL-2kQVVoF-2kQVqYP">
                Image Credit: Nenad Stojkovic @ Flickr
              </a>
            </center>
          </div>
          <div className="col">
            <p>
              So what should the automated check do? If a result is now 6% lower
              than last week, should the build be marked failed or not? That
              would depend on the test and its history. But there's more: What
              if the regression is just 3%, but then another 3% the next week?
            </p>

            <p>
              It is at this point that the valuable time of a skilled
              performance engineering team is wasted in an effort to by hand
              maintain a ruleset of thresholds and variance levels. Experience
              shows this simple idea turns into a losing battle. Even assigning
              a full time engineer will not help, and the nightly performance
              tests continue to have a high degree of both false positives and
              negatives.
            </p>
          </div>
        </div>
        <div className="row col-md-10 offset-md-1">
          <div className="col">
            <h3>More than one way...</h3>
            <p>
              Applying math to the problem can help. Some obvious ideas are to
              compare against a mean of recent results, also taking into account
              the standard deviation of each individual history of metrics.
            </p>

            <p>
              And a moving average is always a good choice for most timeseries -
              also here.
            </p>

            <p>
              Google has patented an interesting sliding window technique
              (2018/0150373 A1, Filed Nov. 28, 2016). This appears to already
              add robustness compared to comparison of two individual points.
              However, if a regression is found this way, it's a limitation that
              the system will only identify a window where the regression was
              introduced, it is unable to identify a specific commit that causes
              the regression.
            </p>
          </div>
        </div>
        <div className="row col-md-10 offset-md-1">
          <div className="col">
            <h3 className="nyrkio-accent">The smart way</h3>
            <p>
              We founded Nyrkiö to help the left shifting of performance testing
              by bringing to general consumption a technique we've found
              superior to all of the above methods.
            </p>

            <p>
              Between the two of us we have over 20 years of experience
              benchmarking and performance tuning the kernel and open source
              databases. We strongly believe that making performance testing a
              part of Continuous Integration is the right way to catch
              regressions as they happen.
            </p>

            <p>
              However, this is only feasible and scalable with sophisticated
              Change Point Detection algorithms that can reliably detect
              regressions and improvements with minimal human effort (per
              build).
            </p>

            <p>
              Nyrkiö is based on work done at{" "}
              <a href="https://github.com/mongodb/signal-processing-algorithms">
                MongoDB
              </a>{" "}
              and <a href="https://github.com/datastax-labs/hunter">Datastax</a>{" "}
              performance engineering teams since 2015,and graciously open
              sourced by both companies for the benefit of all of us. For
              example{" "}
              <a href="https://netflixtechblog.com/fixing-performance-regressions-before-they-happen-eab2602b86fe">
                Netflix also uses the same library in their performance testing
              </a>
              .
            </p>
          </div>
        </div>
        <div className="row mt-4 text-center">
          <center>
            <img
              style={{
                width: "80%",
                border: "#efefeb 10px solid",
                borderRadius: "5px",
              }}
              src={"./src/static/tigerbeetle-change-points.png"}
            />
          </center>
        </div>
        <div className="row col-md-10 offset-md-1 mt-5">
          <p>
            The articles below explain in detail why change detection algorithms
            like e-divisive are superior in solving this problem. The results
            speak for themselves. For example the Mongodb paper reports that
            thanks to this system 17 performance regressions were found and
            fixed during a year of development. Only 1 regression slipped
            through the cracks and was later reported by a customer testing the
            released product.
          </p>

          <p>
            <i>
              Do you already run perf tests in your CI?{" "}
              <a href="/">Create a free account</a> and upload your historical
              data, just to try. You will be amazed at the results.
            </i>
          </p>

          <p>
            <i>
              Not yet running automated perf tests nightly?{" "}
              <a href="mailto:helloworld@nyrk.io">We can help!</a>
            </i>
          </p>
        </div>
        <div className="row col-md-10 offset-md-1">
          <h3>Technical Articles</h3>
          <ul>
            <li>
              <a href="https://arxiv.org/pdf/2003.00584.pdf">
                David Daly et.al.: The Use of Change Point Detection to Identify
                Software Performance Regressions in a Continuous Integration
                System, 2020.
              </a>
            </li>
            <li>
              <a href="https://arxiv.org/pdf/2301.03034.pdf">
                Fleming &amp; Kołaczkowski: Hunter: Using Change Point Detection
                to Hunt for Performance Regressions, 2023.
              </a>
            </li>
            <li>
              <a href="https://arxiv.org/abs/2004.08425">
                Ingo &amp; Daly: Automated System Performance Testing at
                MongoDB. 2020.
              </a>
            </li>
            <li>
              <a href="https://netflixtechblog.com/fixing-performance-regressions-before-they-happen-eab2602b86fe">
                Fixing Performance Regressions Before they Happen
              </a>
              , Angus Croll, Netflix.
            </li>
          </ul>
        </div>
      </div>
    </>
  );
};
