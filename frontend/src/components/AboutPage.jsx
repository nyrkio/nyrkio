import { HenrikCard } from "./people/Henrik.jsx";
import { SannaCard } from "./people/Sanna.jsx";
import { JoeCard } from "./people/Joe.jsx";
import { MattCard } from "./people/Matt.jsx";
import { YoutubeEmbed } from "./Youtube.jsx";
import imgTbChangePoints from "../static/tigerbeetle-change-points-2-trans.png"
import imgGHA from "../static/Nyrkio_GHA.png";

export const AboutPage = () => {
  return (
    <>
      <div className="container about-page">
        <h1 className="text-center text-primary mb-5">About Us</h1>
        <h2 className="h3 text-secondary text-center mb-4 ">Why</h2>
        <p>
          Nyrkiö Oy was founded to commercialize and mainstream <em>Performance Engineering</em>
          tools and methods, that the founders had created in their previous jobs. We believe that
          in many software development projects Performance Engineering is the last hold out for the
          old ways of software development: While all other aspects of the build and testing processes
          have long since been fully democraticed and automated into <em>Continuous Integration</em> and
          <em>Continuous Deployment</em> and <em>DevOps</em> pipelines, performance engineering remains the domain of specialized
          teams of performance experts. These teams often use custom in-house tooling for their work,
          with a low level of automation.</p>
        <p>
          Our vision for Nyrkiö is a future where performance testing is a
          solved problem, with well known mainstream tools available, and
          every developer is in charge of performance of the software they
          write. And all of this as effortlessly as writing a unit test is
          today, and as automatically as triggering a build from a PR happens
          today.
        </p>
        <p>Ultimately, we want to take all the performance testing knowledge and experience,
          all the work we used to do in our past careers,
          and condense it into one more of those green check boxes that you want to see at the bottom of your PR.
        </p>

        <div className="text-center">
          <p className="my-4">
            We call this <b className="text-secondary">Continuous Performance Engineering</b> or <b className="text-secondary">Continuous Benchmarking</b>
          </p>
          <img className="img-fluid border border-2 border-secondary rounded shadow p-4" src={imgGHA} width="422" height="280" alt="Screnshot of check result" />
          <div>
            <a className="btn btn-primary mt-4 mt-md-6" href="https://blog.nyrkio.com/2024/04/17/why-we-started-a-software-performance-company/">Read more</a>
          </div>
        </div>

        <hr className="my-4 my-md-6" />

        <div className="">
          <h2 className="h3 text-center mb-4">Who</h2>
          <div className="row gap-4 gap-xxxl-0">
            <div className="col-xxxl-6 mb-xxxl-6">
              <HenrikCard />
            </div>
            <div className="col-xxxl-6  mb-xxxl-6">
              <SannaCard />
            </div>
            <div className="col-xxxl-6">
              <JoeCard />
            </div>
            <div className="col-xxxl-6">
              <MattCard/>
            </div>
          </div>
        </div>

        <hr className="my-4 my-md-6" />

        <h2 className="h3 text-center text-secondary mb-4">How</h2>
        <p>
          We've been privileged to work on the major <em>open source</em> projects of
          our lifetime: Linux, MySQL, MongoDB, Cassandra... and so many
          smaller projects and utilities! Nyrkiö is no different.{" "}<br className="d-none d-md-block"/>
          <a href="https://github.com/nyrkio/">
            You can follow along, or join us, at Github
          </a>
          .
        </p>
        <p>
        After meeting with several investors in the first year of operations, we've ended up as a self funded startup,
        with no outside investors, at least for now. One reason for this is that we didn't want to impose on ourselves
        some artificial deadline coming from the investment fund's expiration date. We're here to transform the performance
        engineering industry. It might take some time, but we aren't going anywhere, we are here for the long term.
        </p>
        <p>For example, this has allowed us to adopt a principle where we always prioritize our existing customers needs
           before we spend time on new customer acquisition. Thanks to this, our subsciption renewal rate in the first years
           has been a perfect 100%</p>

        <hr className="my-4 my-md-6" />

        <h2 className="h3 text-center text-secondary">Where</h2>
        <p>For legal and tax purposes, Nyrkiö is headquartered in Järvenpää, Finland. Like many open source companies before us,
        we work in distributed teams, "remotely" as they say today, and hire the best people we
        can find, wherever they happen to live.
        </p>
        <YoutubeEmbed embedId="v1Cu5LUWTpw"/>

        <hr className="mt-4 mt-md-6" />
      </div>
    </>
  );
};
