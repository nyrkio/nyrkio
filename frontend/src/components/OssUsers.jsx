const cols = "col-sm-6 col-md-4";
const style = {paddingRight: "2em"};

export const MongoDB = () => {
    return (<>
    <div className={cols} style={style}>
    <h4>MongoDB</h4>
    <p>The MongoDB performance team is the home of this idea, and the core math that is the <em>E-Divisive Means</em> algorithm was implemented there.</p>
    <p>After almost a decade in production use, the shift to <em>Continuous Performance Engineering</em> has unlocked a culture where responsibility for performance benchmarks and fixing regressions has been delegated down to individual feature teams. Nowadays MongoDB automatically analyzes over a million data points per build, produceed by their automated performance testing framework. This is only possible thanks to finding an algorithm that allows for automatic processing of results with a low false positive rate.</p>

    <p>Read more...</p>

    <ul>
    <li><a href="https://arxiv.org/abs/2003.00584">Change Point Detection in Software Performance Testing</a>, Daly et.al., 2020.</li>
    <li><a href="https://arxiv.org/abs/2004.08425">Automated System Performance Testing at MongoDB</a>, Ingo & Daly, 2020.</li>
    <li><a href="https://dl.acm.org/doi/10.1145/3427921.3450234">Creating a Virtuous Cycle in Performance Testing at MongoDB</a>, Daly, 2021.</li>
    <li><a href="https://www.mongodb.com/company/blog/mongodb-8-0-improving-performance-avoiding-regressions">MongoDB 8.0: Improving Performance, Avoiding Regressions</a>, Mark Benvenuto, 2025.</li>
    </ul>
    </div>
    </>
    );
};


export const Netflix = () => {
    return (<>
    <div className={cols} style={style}>
    <h4>Netflix</h4>
    <p>At Netflix maintaining reliable performance is paramount to the end user experience. A sluggish transfer between UI screens could lead to users abandoning the service altogether, or in any case usability will suffer. Netflix runs on TVs and set top boxes, which have less resources than a laptop or PC. Hence the environment is more sensitive to performance issues, and performance regressions may have very visible consequences, including crashing the Netflix app entirely.</p>
    <p>The Netflix TVUI team was the first company to use the Change Point Detection algorithm developed and open sourced at MongoDB.</p>

    <p>Read more...</p>

    <ul>
    <li><a href="https://netflixtechblog.com/fixing-performance-regressions-before-they-happen-eab2602b86fe">Fixing Performance Regressions Before they Happen</a>, Angus Croll, 2022</li>
    <li><a href="https://bismabhundi.medium.com/netflix-a-shining-example-of-qa-done-right-c566196dfceb">Netflix: A Shining Example of QA Done Right</a>, Bisma Latif, 2024.</li>
    <li><a href="https://www.reddit.com/r/programming/comments/teddg5/netflix_fixing_performance_regressions_before/">Netflix: Fixing Performance Regressions Before they Happen</a>, Reddit, 2022.</li>
    </ul>
    </div>
    </>
    );
};

export const Datastax = () => {
    return (<>
    <div className={cols} style={style}>
    <h4>Datastax</h4>
    <p>Datastax, just like MongoDB, had taken the step to automate a suite of performance tests, aka <em>Continuous Performance Engineering</em>. The results of nightly builds would be stored in a Grafana / Prometheus database and dashboard, and a human engineer would look at the dashboards every now and then. When MongoDB published their paper on using Change Point Detection to analyze such results, Datastax engineers were eager to automate also the analysis part of the work.</p>
    <p>Datastax built upon the E-Divisive algorithm open sourced by MongoDB, and made major additions. Datastax also published their work in the same conference as MongoDB had done, and open sourced their additions as MongoDB had done. This transformed what was essentially a math or signal processing library, to a fully functional command-line tool, that can read and output CSV files, and several database sources, such as Postgresql.</p>

    <p>Read more...</p>

    <ul>
    <li><a href="https://arxiv.org/abs/2301.03034">Hunter: Using Change Point Detection to Hunt for Performance Regressions</a>, Fleming & Kołaczkowski, 2024.</li>
    <li><a href="https://medium.com/building-the-open-data-stack/detecting-performance-regressions-with-datastax-hunter-c22dc444aea4">Detecting Performance Regressions with DataStax Hunter</a>, Piotr Kołaczkowski</li>
    </ul>
    </div>
    </>
    );
};


export const Confluent = () => {
    return (<>
    <div className={cols} style={style}>
    <h4>Confluent</h4>
    <p>Confluent uses Apache Otava as part of a Continuous Benchmarking workflow to test performance of Kafka Streams. The streaming of data requires extreme performance, as Kafka clusters kan scale to dozens of nodes, and millions of messages per second.</p>

    <p>Reading list</p>

    <ul>
    <li><a href="https://www.confluent.io/events/kafka-summit-london-2024/automating-speed-a-proven-approach-to-preventing-performance-regressions-in/">Automating Speed: A Proven Approach to Preventing Performance Regressions in Kafka Streams</a>, Alexander Sorokoumov & John Roessler, 2024</li>
    </ul>
    </div>
    </>
    );
};




export const RedHat = () => {
    return (<>
    <div className={cols} style={style}>
    <h4>Red Hat OpenShift</h4>
    <p>OpenShift is Red Hat's Kubernetes platform. It is a basic Infrastructure as a Service and naturally customers expect reliable performance and no surprises.</p>
    <p>Red Hat uses Apache Otava as part of Cloud Bulldozer, a performance testing and results analysis framework. The results  are made available to the OpenShift community. This way everyone benefits from the results of Red Hat's Continuous Benchmarking efforts.</p>

    <p>Read more...</p>

    <ul>
    <li><a href="https://github.com/cloud-bulldozer">https://github.com/cloud-bulldozer</a></li>
    </ul>
    </div>
    </>
    );
};


