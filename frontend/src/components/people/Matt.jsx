export const MattCard = () => {
  return (
            <div className="row row-cols-1 row-cols-md-2">
            <div className="col">
            <div className="card m-3 rounded-3 shadow people-card">
              <div className="card-header p-5 justify-content-center text-center">
                <img src="/src/static/people/Matt-600x800.jpg" alt="Head shot"
                     className="rounded-3"/>
                <h4 className="my-2">Matt Fleming</h4>
                <p>CTO</p>
              </div>
              </div>
            </div>
            <div className="col p-4">
              <p>Matt has worked most of his career with the Linux kernel, including as the subsystem
              maintainer while employed at Intel and SUSE. During his years at SUSE,
              he became a well known authority on Linux performance.</p>
              <p>Due to his performance work at SUSE, Matt was an early reader of the
              change detection paper Henrik had co-authored, and this is how the founders met.
              Soon after Matt joined Henrik at Datastax, where he worked on analyzing and solving
              scaling issues reported by the largest customers, and eventually lead the entire core
              database team in an effort to contribute major performance improvements into Cassandra 5.0.
              At Datastax Matt and Henrik also co-authored a second paper on change detection.</p>
              <p>At Nyrkiö Matt leads the product development of the Nyrkiö platform. He also works with
              our customers helping them on their journey to automate performance testing in nightly builds,
              Continuous Integration and Pull Requests.
              </p>
            </div>
          </div>
  );
};
