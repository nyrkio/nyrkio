import imgStars from "../static/tahdenlento_blogi.webp";
import imgGHA from "../static/Nyrkio_GHA.png";

import { MongoDB, Netflix, Datastax, Confluent, RedHat } from "./OssUsers.jsx"

export const EcosystemPage = () => {
  return (<>
  <div className="container section-ecosystem">
  <div className="row">
    <div className="col-sm-12 col-xl-12 mt-8">
        <h1 className="mb-5">Open Source Ecosystem</h1>
        <p>Nyrkiö is based on open source performance tools that Henrik and Matt have been involved in developing as part of their previous jobs,
        working in the performánce engineering teams at MongoDB, Datastax, and others. <a href="https://blog.nyrkio.com/2025/05/08/welcome-apache-otava-incubating-project/">Read more about the history of Apache Otava on the Nyrkiö blog</a>.
        </p>
        </div>

        <div className="row">
        <div className="col-sm-2 col-md-3 col-lg-4"><img src={imgStars} style={{maxWidth: "85%", margin: "1em", marginTop: "9em", objectFit: "scale-down", borderRadius: "10px"}}/></div>
        <div className="col-sm-10 col-md-9 col-lg-8">
        <h2>Apache Otava (incubating)</h2>
        <p>Originally known as Hunter, this code was written by Piotr Kołaczkowski at Datastax, and Datastax has eventually kindly donated the project to the Apache Software Foundation, to allow other users to contribute their improvements and to allow the project to grow. A proto-version of what is today Apache Otava was first used in production at MongoDB around 2017. After MongoDB published the code as open source, in 2020, Netflix and Datastax were quick to follow.</p>
        <ul>
          <li>Checkout the <a href="https://otava.apache.org">project website</a>,</li>
          <li><a href="https://otava.apache.org/docs/overview/">read the documentation</a>,</li>
          <li><a href="https://pypi.org/project/apache-otava/">PyPI page</a>, to</li>
          <li><a href="https://pypi.org/project/apache-otava/#files">download and test it</a></li>
          <li><a href="https://otava.apache.org/docs/community">Join the mailing list...</a></li>
          </ul>
        <p>...and contribute! Opinions, ideas, bug reports and patches are all valued ways of contributing to open source.</p>

        </div>
        </div>
        <div className="row">
        <div className="col-sm-4 col-md-3 col-lg-2"></div>
        <h3>Users</h3>
        <MongoDB />
        <Netflix />
        <Datastax />
        <Confluent />
        <RedHat />

        </div>
        </div>
        </div>

        <div className="row" style={{marginTop: "9em"}}>
        <div className="col-sm-10 col-md-9 col-lg-8">
        <h2>GitHub Action Benchmark</h2>
        <p>GitHub Action Benchmark is an open source project developed over the past 6 years to simplify results analysis and alerting in continuous performance engineering workflows. GHABenchmark uses simple threshold based comparison. (Today's result is X% less than yesterday.) This is where Nyrkiö can make a significant difference. For the better! On the other hand by using this open source tool, Nyrkiö gains integrations with all the major performance benchmark frameworks that are supported by GHA Benchmark.</p>
        <ul>
        <li><a href="https://github.com/benchmark-action/github-action-benchmark">GitHub repo</a>,</li>
        <li><a href="https://benchmark-action.github.io/github-action-benchmark/dev/bench/">Dashboard</a>,</li>
        </ul>
        </div>
        <div className="col-sm-2 col-md-3 col-lg-4"><img src={imgGHA} style={{maxWidth: "85%", border: "solid 4px darkgray", margin: "1em", marginTop: "9em", objectFit: "scale-down", borderRadius: "10px"}}/></div>
        </div>
  </>);
};
