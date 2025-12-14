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
        <div className="row col-xl-12 mt-2 p-3">
          <h1 className="text-center mb-5">About Us</h1>
          <h2>Why</h2>
          <p>
            Nyrkiö Oy was founded to commercialize and mainstream <em>Performance Engineering</em>
            tools and methods, that the founders had created in their previous jobs. We believe that
            in many software development projects Performance Engineering is the last hold out for the
            old ways of software development: While all other aspects of the build and testing processes
            have long since been fully democraticed and automated into <em>Continuous Integration</em> and
            <em>Continuous Deployment</em> pipelines, performance engineering remains the domain of specialized
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
          <p>We call this <em>Continuous Performance Engineering</em> or <em>Continuous Benchmarking</em></p>

          <div className="col-sm-2 col-md-3 col-lg-4"><img src={imgGHA} style={{maxWidth: "85%", border: "solid 4px darkgray", margin: "1em", objectFit: "scale-down", borderRadius: "10px"}}/></div>
          <p>
            <a href="https://blog.nyrkio.com/2024/04/17/why-we-started-a-software-performance-company/">
              Read more about why we started Nyrkiö...
            </a>
          </p>

        </div>
        <div className="row w-100 who">
        <h2>Who</h2>
        <div className="col-xs-12 col-md-10 col-lg-6">
          <HenrikCard />
        </div>
        <div className="col-xs-12 col-md-10 col-lg-6">
          <SannaCard />
          </div>
          <div className="col-xs-12 col-md-10 col-lg-6">
          <JoeCard />
          </div>
          <div className="col-xs-12 col-md-10 col-lg-6">
          &nbsp;
          </div>
          <div className="col-xs-12 col-md-10 col-lg-6">
          <MattCard/>
          </div>
        </div>
        <div className="row justify-content-center">
          <h2>How</h2>
          <p>
            We've been privileged to work on the major <em>open source</em> projects of
            our lifetime: Linux, MySQL, MongoDB, Cassandra... and so many
            smaller projects and utilities! Nyrkiö is no different.{" "}
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
          <h2>Where</h2>
          <p>For legal and tax purposes, Nyrkiö is headquartered in Järvenpää, Finland. Like many open source companies before us,
          we work in distributed teams, "remotely" as they say today, and hire the best people we
          can find, wherever they happen to live.
          </p>
          <YoutubeEmbed embedId="v1Cu5LUWTpw"/>
        </div>
      </div>
    </>
  );
};
