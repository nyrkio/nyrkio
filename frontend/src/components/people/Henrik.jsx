export const HenrikCard = () => {
  return (
            <div className="row row-cols-2">
            <div className="col">
            <div className="card m-3 rounded-3 shadow people-card">
              <div className="card-header p-3">
                <img src="/src/static/people/Henrik-600x800.jpg" alt="Head shot"
                     className="w-100 rounded-3 "/>
                <h4 className="my-0 fw-normal">Henrik Ingo</h4>
                <p>CEO</p>
              </div>
              </div>
            </div>
            <div className="col">
            <div className="card m-3 rounded-3 shadow people-card">
              <div className="card-body p-3 justify-content-center text-justify h-100">
              <p>Henrik has worked two decades in the world of Open Source databases: MySQL, MariaDB, MongoDB, Cassandra, Postgresql...
              He is known for his interest in performance and scaling, including topics like distributed consensus algorithms.</p>
              <p>He has worked both in sales and engineering and both as a manager and engineer, giving him a broad experience that
              is helpful as an entrepreneur gets to do a little bit of everything.</p>
              <p>Henrik worked on the MongoDB performance engineering team in 2015, where the E-Divisive algorithm was first used
              for automating the detection of performance regressions, and eventually published as both a conference paper and
              open source code. Later he managed the performance team at Datastax, where further improvements were implemented
              and again open sourced. Now Nyrkiö is bringing that work into the mainstream.</p>
              </div>
              </div>
            </div>
          </div>
  );
};
