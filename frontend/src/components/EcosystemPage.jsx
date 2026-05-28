import imgStars from "../static/tahdenlento_blogi.webp";
import imgGHA from "../static/Nyrkio_GHA.png";

import { OssUserSlider } from "./OssUsers.jsx"

export const EcosystemPage = () => {
  return (<>
    <div className="container section-ecosystem">
      <div className="text-center mb-section">
        <h1 className="text-primary mb-5">Open Source Ecosystem</h1>
        <p className="mb-5">Nyrkiö is based on open source performance tools that Henrik and Matt have been involved in developing as part of their previous jobs,
          working in the performánce engineering teams at MongoDB, Datastax, and others.
        </p>
        <a className="btn btn-primary" href="https://blog.nyrkio.com/2025/05/08/welcome-apache-otava-incubating-project/" target="_blank" rel="noopener noreferrer">Read more</a>
      </div>

      <div className="row">
        <div className="col-md-4">
          <div className="border border-2 border-secondary rounded-3 shadow p-3 p-md-4">
            <img src={imgStars} className="img-fluid rounded-2" alt="Space banner" />
          </div>
        </div>
        <div className="col-md-8">
          <h2 className="h3 text-secondary mb-3 mb-md-4">Apache Otava (incubating)</h2>
          <p>Originally known as Hunter, this code was written by Piotr Kołaczkowski at Datastax, and Datastax has eventually kindly donated the project to the Apache Software Foundation, to allow other users to contribute their improvements and to allow the project to grow. A proto-version of what is today Apache Otava was first used in production at MongoDB around 2017. After MongoDB published the code as open source, in 2020, Netflix and Datastax were quick to follow.</p>
          <ul>
            <li>Checkout the <a href="https://otava.apache.org" target="_blank" rel="noopener noreferrer">project website</a>,</li>
            <li><a href="https://otava.apache.org/docs/overview/" target="_blank" rel="noopener noreferrer">read the documentation</a>,</li>
            <li><a href="https://pypi.org/project/apache-otava/" target="_blank" rel="noopener noreferrer">PyPI page</a>, to</li>
            <li><a href="https://pypi.org/project/apache-otava/#files" target="_blank" rel="noopener noreferrer">download and test it</a></li>
            <li><a href="https://otava.apache.org/docs/community" target="_blank" rel="noopener noreferrer">Join the mailing list</a></li>
          </ul>
          <p>and contribute! Opinions, ideas, bug reports and patches are all valued ways of contributing to open source.</p>
        </div>
      </div>

      <hr className="my-4 my-md-6" />

      <h2 className="h3 text-secondary text-center">Users</h2>

      <OssUserSlider/>


      <h2 className="text-center text-primary mt-section">GitHub Action Benchmark</h2>
      <p>GitHub Action Benchmark is an open source project developed over the past 6 years to simplify results analysis and alerting in continuous performance engineering workflows. GHABenchmark uses simple threshold based comparison. (Today's result is X% less than yesterday.) This is where Nyrkiö can make a significant difference. For the better! On the other hand by using this open source tool, Nyrkiö gains integrations with all the major performance benchmark frameworks that are supported by GHA Benchmark.</p>
      <div className="d-flex justify-content-center">
        <ul className="my-5">
          <li><a href="https://github.com/benchmark-action/github-action-benchmark" target="_blank" rel="noopener noreferrer">GitHub repo</a>,</li>
          <li><a href="https://benchmark-action.github.io/github-action-benchmark/dev/bench/" target="_blank" rel="noopener noreferrer">Dashboard</a>,</li>
        </ul>
      </div>


      <img className="img-fluid border d-block mx-auto border-2 border-secondary rounded-3 shadow p-3 p-md-4"
           loading="lazy"
           alt="Screenshot of GitHub progress indicator"
           width="422"
           height="280"
           src={imgGHA}/>
    </div>
  </>);
};
