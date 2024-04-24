import { HenrikCard } from "./people/Henrik.jsx";
import { MattCard } from "./people/Matt.jsx";
import { YoutubeEmbed } from "./Youtube.jsx"

export const AboutPage = () => {

  return (
    <>
      <div className="container about-page">
        <div className="row col-xl-10 mt-8 p-5">
          <h1 className="text-center mb-5">
            About Us
          </h1>
          <h2>Why</h2>
          <p>Nyrkiö Oy is a startup founded by two friends, software developers and performance
             experts, Henrik Ingo and Matt Fleming.</p>
          <p>Our background is in open source, Linux and databases. For the past two decades we've
             worked on small embedded systems to distributed database clusters with hundreds of
             nodes and petabytes of data. Fault tolerance, distributed consensus, device drivers...</p>
          <p>But what we are best known for, and how we met each other, is our work on software
             performance. <span className="nyrkio-accent"><strong>We started Nyrkiö to bring our experience, and the tools
             we've developed and used over the years, into the mainstream.</strong></span></p>
          <p>Our vision for Nyrkiö is
             a future where performance testing is a solved problem, with well known mainstream
             tools available, and every developer is in charge of performance of the software they
             write. And all of this as effortlessly as writing a unit test is today, and as
             automatically as triggering a build from a PR happens today.
             </p>
          <p><a href="https://blog.nyrkio.com/2024/04/17/why-we-started-a-software-performance-company/">Read more about why we started Nyrkiö...</a></p>
          <h2>Where</h2>
          <p>We've worked most of our adult lives remotely, or <em>distributed</em>, as we prefer to
             call it. Nyrkiö will likewise be a distributed company, hiring the best people for each
             job, regardless of where in the world they are living.</p>
          <p>For legal and tax purposes, Nyrkiö Oy is headquartered in Järvenpää, Finland.</p>
          <p>Matt lives and works out of Halifax, United Kingdom.</p>
          <p><a href="/contact">Contact us...</a></p>
          <YoutubeEmbed embedId={"v1Cu5LUWTpw"} />
          <h2>How</h2>
          <p>We've been privileged to work on the major open source projects of our lifetime: Linux,
          MySQL, MongoDB, Cassandra... and so many smaller projects and utilities! Nyrkiö is no
          different. <a href="https://github.com/nyrkio/">You can follow along, or join us, at
          Github</a>.</p>
          <p>To maximize our autonomy as entrepreneurs, and yes, our commitment to open source is
          part of that, we have decided to bootstrap Nyrkiö with our own work and savings, without
          external investment. Until <a href="/pricing">product revenue</a> grows large enough to
          cover our salaries, we offer a range of <a href="/services">consulting services</a> to
          pay our own salaries.</p>
          <h2>Who</h2>
        </div>
        <div className="col-xl-10 justify-content-center">
        <HenrikCard />
        <MattCard />
        </div>
      </div>
    </>
  );
};
