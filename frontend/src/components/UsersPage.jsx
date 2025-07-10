export const UsersPage = () => {
  return (<>
    <div className="row">
    <Turso />
    <Dremio />
    </div>
    </>)
};


const cols = "col-sm-12 col-md-6 col-xl-4 nyrkio-user-card";
const style = {paddingRight: "3em", marginTop: "4em"};
const imgStyle = {maxWidth: "300px", maxHeight: "300px", borderRadius: "50px"};
const imgTitleStyle = {textAlign: "center", height: "300px", paddingRight: "1.5em"};


import tursoLogo from "../static/turso-banner.png";
export const Turso = () => {
    return (<>
    <div className={cols} style={style}>
    <h4 style={imgTitleStyle}><img src={tursoLogo} style={imgStyle} /></h4>
    <p>Turso Database is an active open source project that is rewriting good old SQLite in Rust. With over 200 contributors each month, this project is merging a dozen patches each day. To move fast with confidence they need airthight test coverage also for performance. TPC-H, Clickbench and various self made test queries run after each merge. The company behind the open source project is also operating a Database as a Service.</p>


    <ul>
    <li>
    <a href="/public/https%3A%2F%2Fgithub.com%2Ftursodatabase%2Flimbo/main/">View public benchmark results from Turso</a>
    </li>
    <li>
    <a href="https://www.youtube.com/watch?v=iiS0KoYc_Zc">Pekka (founder of Turso Database) and Henrik (founder of Nyrkiö) went to a bar...</a>
    </li>
    </ul>
    </div>
    </>
    );
};

import dremioLogo from "../static/dremio_logo.png";
export const Dremio = () => {
    return (<>
    <div className={cols} style={style}>
    <h4 style={imgTitleStyle}><img src={dremioLogo} style={imgStyle} /></h4>
    <p>Dremio develops and sells Big Data solutions based on Apache Iceberg. To ensure that there aren't any performance regressions, a TPC-H benchmark is run weekly. Dremio were one of the first users to try Nyrkio the very same day we launched, and when testing Nyrkiö with some old benchmark results,
    Nyrkiö was able to find a regressionn the team had not noticed before!</p>


    <ul>
    <li>
    <a href="https://blog.nyrkio.com/2025/03/25/interview-with-pierre-laporte-part-i/">Interview with Pierre Laporte (part 1)</a>
    </li>
    <li>
    <a href="https://blog.nyrkio.com/2025/03/31/interview-with-pierre-laporte-part-2/">Interview with Pierre Laporte (part 2)</a>
    </li>
    </ul>
    </div>
    </>
    );
};
