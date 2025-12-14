import headShot from "../../static/people/Joe-600x800.jpg";

export const JoeCard = () => {
  return (
    <div className="row row-cols-1 row-cols-md-2">
      <div className="col">
        <div className="card m-3 rounded-3 shadow people-card">
          <div className="card-header p-5 justify-content-center text-center">
            <img src={headShot} alt="Head shot" className="rounded-3" />
            <h4 className="my-2">Joe Drumgoole</h4>
            <p>Developer Relations</p>
          </div>
        </div>
      </div>
      <div className="col p-4">
        <p>

        </p>
        <p>
        From Oracle to founding startups of his own, Joe brings with him decades of experience from the Dublin tech scene. Joe and Henrik met in 2013 when MongoDB expanded to Europe and assembled a "dream team" of database experts that the European database industry had not seen before, and probably never will. Most recently Joe worked at PostgreSQL shop Neon.
        </p>
        <p>At Nyrkiö Joe has a "player-coach" role. Part advisor to the CEO on marketing and Go-To-Market approach, part hands on developer relations projects. With a little help from AI, Joe caught up 2 years worth of technical debt, in a single 100 thousand line patch of playwright tests! All those tests we promised to add "later"... we finally did!</p>
      </div>
    </div>
  );
};
