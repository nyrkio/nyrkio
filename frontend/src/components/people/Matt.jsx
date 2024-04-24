export const MattCard = () => {
  return (
            <div className="row row-cols-2">
            <div className="col">
            <div className="card m-3 rounded-3 shadow people-card">
              <div className="card-header p-3">
                <img src="/src/static/people/Matt-600x800.jpg" alt="Head shot"
                     className="w-100 rounded-3 "/>
                <h4 className="my-0 fw-normal">Matt Fleming</h4>
                <p>CTO</p>
              </div>
              </div>
            </div>
            <div className="col">
            <div className="card m-3 rounded-3 shadow people-card">
              <div className="card-body p-3 justify-content-center text-justify h-100">
              <p>Matt has worked most of his career with the Linux kernel, including as the subsystem
              maintainer while at Intel. During his years at Suse,
              he became a well known authority on Linux performance.</p>
              <p>Due to his performance work at Suse, Matt was an early reader of the
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
            </div>
          </div>
  );
};
