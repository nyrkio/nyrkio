import { CpuHours } from "../PricingPage";
import select1after from "../../static/runner/turso_select1_nyrkiorunner.png";
import select1before from "../../static/runner/turso_select1_ghrunner.png";

export const Mission = ({loggedIn}) => {
  return (
    <>
      <section className="my-section container">
        <div className="row align-items-center gap-4 gap-md-0 mb-6">
          <div className="col-12">
            <h2 className="text-primary text-center mb-3 mb-md-5">
              <div className="h3 text-secondary mb-2">New:</div>
              Nyrkiö Runner for GitHub
            </h2>
          </div>
          <div className="col-12 col-md-6 pe-lg-7">
            <h3 className="h6 text-secondary fw-semibold">Do you struggle with noisy benchmark results?</h3>
            <p>It's hard to spot real regressions if your noise range is 50%, yet this is a common situation for many.</p>
            <p>At Nyrkiö we have a decade of experience how to tune a server for maximum stability and repeatability. Our customers are achieving benchmark results that stay within 1 nanosecond from build to build!</p>
          </div>
          <div className="col-12 col-md-6">
            <img loading="lazy" className="img-fluid" src={select1before} alt="A noisy graph from Nyrkio dashboard" title="Turso SELECT 1 benchmark. Spikes are up to 100 ns, noise range = 40%"/>
          </div>
        </div>

        <div className="row align-items-center gap-4 gap-md-0">
          <div className="col-12 col-md-6">
            <h3 className="text-secondary">1. Install Nyrkiö in your GitHub org</h3>
            <p>Currently self hosted runners are supported only for repositories that belong to an org. We are working on a solution to also support repos in your personal namespace without needing excessive permissions to do so.</p>
            <a className="btn btn-outline-primary mt-4 d-block d-lg-inline-block" href="https://github.com/apps/nyrkio/installations/new">github.com</a>
          </div>
          <div className="col-12 col-md-6">
            <img loading="lazy" className="img-fluid d-block m-auto w-75 w-md-100 w-lg-75 w-xl-50" src="/p/NyyrikkiRunner/squirrel5.webp" alt="Nyrkiö Runner"/>
          </div>
        </div>

        <hr className="my-5"/>

        <div className="row align-items-center gap-4 gap-md-0">
          <div className="col-12 col-md-6">
            <h3 className="text-secondary">2. Select a subscription level</h3>
            <p>With consumption based subscription, you only pay for how many minutes you used the servers. Typically less than 10 € / month.</p>
            <a className="btn btn-outline-primary mt-4 d-block d-lg-inline-block" href="/pricing">All Pricing</a>

          </div>
          <div className="col-12 col-md-6 d-md-flex justify-content-md-center">
            <div style={{minWidth: '320px'}}>
              <CpuHours loggedIn={loggedIn} short={true} />
            </div>
          </div>
        </div>

        <hr className="my-5"/>
        <div className="row align-items-center gap-4 gap-md-0">
          <div className="col-12 col-md-6">
            <h3 className="text-secondary">3. Choose a runner</h3>
            <p>Lastly: Replace the <span className="badge" style={{backgroundColor: '#50320DB2', fontSize: 'inherit', fontWeight: 'inherit'}}>runs-on: ubuntu-latest</span> with <span className="badge" style={{backgroundColor: '#50320DB2', fontSize: 'inherit', fontWeight: 'inherit'}}>runs-on: nyrkio_4</span> </p>
            <p>Your tests will now run on Nyrkiö test runners, and typically you'll see the <span className="nyrkio-accent">noise range in your benchmarks decrease by an order of magnitude!</span></p>
          </div>
          <div className="col-12 col-md-6">
            <img className="img-fluid" loading="lazy" src={select1after} alt="Less noisy graph from Nyrkio dashboard, using Nyrkio runners" title="Turso SELECT 1 benchmark. Variation within 9 ns, noise range = 5%"/>
          </div>
        </div>
      </section>
    </>
  );
};
