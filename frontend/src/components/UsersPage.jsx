export const UsersPage = () => {
  return (<>
    <div className="row">
    <Turso />
    <Dremio />
    <Tigerbeetle />
    <hr />
    <div className="row">
    <p>Want more? Read about how Netflix, Confluent, RedHat, MongoDB, DataStax and Tarantool use Change Point Detection in their Continuous Performance Engineering workflows over at <a href="/about/ecosystem">our Open Source Ecosystem page</a>.</p>
    </div>
    </div>
    </>)
};


const cols = "col-sm-12 col-lg-6 col-xl-4 nyrkio-user-card";
const style = {paddingLeft: "1em", paddingRight: "3em", marginTop: "10em"};
const imgStyle = {maxWidth: "300px", maxHeight: "300px", borderRadius: "50px"};
const imgTitleStyle = {textAlign: "center", height: "250px", paddingRight: "1.5em"};

export const TursoQuote = () =>{
    return (
    <div className="row nyrkio-user-photo-quote">
    <p><img src={tursoPekka} style={{maxWidth: "100%"}} className="col-xs-12 col-lg-6"/>
    <br />
    <span style={{fontSize: "4em"}}>&nbsp;</span>
    <br />

    <q>Good news is we finally have Nyrkiö configured for Turso. And it detects our improvements too! Bad news is that we [didn't do it sooner...]</q></p>
    <p className="user quote-attribution">Pekka Enberg, Founder, Turso Database</p>
    </div>
    );

};

import tursoLogo from "../static/turso-banner.png";
import tursoPekka from "../static/people/PekkaEnberg-600x800.jpg";
export const Turso = () => {
    return (<>
    <div className={cols} style={style}>
    <TursoLogo />
    <TursoDescription />
    <TursoQuote />
    <TursoLinks />
    </div>
    </>);
};

export const TursoMini = () => {
    return (<>
        <TursoLogo />
        <TursoQuote />
        <ul>
        <li>
        <a href="/public/https%3A%2F%2Fgithub.com%2Ftursodatabase%2Flimbo/main/">View public benchmark results from Turso</a>
        </li>
        </ul>
        </>);
};

export const TursoLogo = () => {
    return (<h4 style={imgTitleStyle}><img src={tursoLogo} style={imgStyle} /></h4>);
};
export const TursoDescription = () => {
    return (<>
    <p>Turso Database is an active open source project that is rewriting good old SQLite in Rust. With over 200 contributors each month, this project is merging a dozen patches each day. To move fast with confidence they need airthight test coverage also for performance. TPC-H, Clickbench and various self made test queries run after each merge. The company behind the open source project is also operating a Database as a Service.</p>
    </>);
};

export const TursoLinks = () => {
    return (<>
    <ul>
    <li>
    <a href="/public/https%3A%2F%2Fgithub.com%2Ftursodatabase%2Flimbo/main/">View public benchmark results from Turso</a>
    </li>
    <li>
    <a href="https://www.youtube.com/watch?v=iiS0KoYc_Zc">Pekka (founder of Turso Database) and Henrik (founder of Nyrkiö) went to a bar...</a>
    </li>
    </ul>
    </>
    );
};


export const DremioQuote = () =>{
    return (
    <div className="row nyrkio-user-photo-quote">
    <p><img src={dremioPierre} style={{maxWidth: "100%"}} className="col-xs-12 col-lg-6"/>
    <br />
    <span style={{fontSize: "4em"}}>&nbsp;</span>
    <br />

    <q>Nyrkiö is able to detect change points even in high-variance data.
    So that solved the first challenge entirely.  We could focus on reducing the variance with the piece of mind
    that detection was a solved problem.</q></p>
    <p className="user quote-attribution">Pierre Laporte, Senior Staff Performance Engineer, Dremio</p>
    </div>
    );
};

import dremioLogo from "../static/dremio_logo.png";
import dremioPierre from "../static/people/Pierre-Dog-600x800.jpg";
export const Dremio = () => {
    return (<>
    <div className={cols} style={style}>
    <DremioLogo />
    <DremioDescription />
    <DremioQuote />
    <DremioLinks />
    </div>
    </>
    );
};

export const DremioMini = () => {
    return (<>
    <DremioLogo />
    <DremioQuote />
    <ul>
    <li>
    <a href="https://nyrkio.com/public/https%3A%2F%2Fgithub.com%2Ftigerbeetle%2Ftigerbeetle/main/devhub">Dremio public benchmark results on Nyrkiö</a>
    </li>
    </ul>
    </>);
};

export const DremioLogo = () => {
    return (<h4 style={imgTitleStyle}><img src={dremioLogo} style={imgStyle} /></h4>);
};
export const DremioDescription = () => {
    return (<>
    <p>Dremio develops and sells Big Data solutions based on Apache Iceberg. To ensure that there aren't any performance regressions, a TPC-H benchmark is run weekly. Dremio were one of the first users to try Nyrkio the very same day we launched, and when testing Nyrkiö with some old benchmark results,
    Nyrkiö was able to find a regression the team had not noticed before!</p>
    </>);
};

export const DremioLinks = () => {
    return (<>
    <ul>
    <li>
    <a href="https://blog.nyrkio.com/2025/03/25/interview-with-pierre-laporte-part-i/">Interview with Pierre Laporte (part 1)</a>
    </li>
    <li>
    <a href="https://blog.nyrkio.com/2025/03/31/interview-with-pierre-laporte-part-2/">Interview with Pierre Laporte (part 2)</a>
    </li>
    </ul>
    </>
    );
};


export const TigerbeetleQuote = () =>{
    return (
        <div className="row nyrkio-user-photo-quote">
        <p><img src={tigerbeetleJoran} style={{maxWidth: "100%"}} className="col-xs-12 col-lg-6"/>
        <br />
        <span style={{fontSize: "4em"}}>&nbsp;</span>
        <br />

        <q>Nyrkiö did a better job than our internal graphs.</q></p>
        <p className="user quote-attribution">Joran Dirk Greef, Founder & CEO, Tigerbeetle</p>
        </div>
    );
};

import tigerbeetleLogo from "../static/tb-logo-black.png";
import tigerbeetleJoran from "../static/people/Joran-600x800.jpg";
export const Tigerbeetle = () => {
    return (<>
    <div className={cols} style={style}>
    <TigerbeetleLogo />
    <TigerbeetleDescription />
    <TigerbeetleQuote />
    <TigerbeetleLinks />
    </div>
    </>
    );
};

export const TigerbeetleMini = () => {
    return (<>
    <TigerbeetleLogo />
    <TigerbeetleQuote />
    <ul>
    <li>
    <a href="https://nyrkio.com/public/https%3A%2F%2Fgithub.com%2Ftigerbeetle%2Ftigerbeetle/main/devhub">Tigerbeetle public benchmark results on Nyrkiö</a>
    </li>
    </ul>
    </>);
};

export const TigerbeetleLogo = () => {
    return (<h4 style={imgTitleStyle}><img src={tigerbeetleLogo} style={imgStyle} /></h4>);
};
export const TigerbeetleDescription = () => {
    return (<>
    <p>TigerBeetle is a specialized transactions database, designed for safety and 1000x performance, to power the future of online transaction processing (OLTP). The architecture is based on the realization that batching multiple transactions into one large commit can achieve much faster velocity than a traditional general purpose database. A notable property in Tigerbeetle's use of Nyrkiö: they track 100% percentile latency (so max latency) and variation in this is
    considered a regression!</p>
    </>);
};

export const TigerbeetleLinks = () => {
    return (<>
    <ul>
    <li>
    <a href="https://nyrkio.com/public/https%3A%2F%2Fgithub.com%2Ftigerbeetle%2Ftigerbeetle/main/devhub">Tigerbeetle public benchmark results on Nyrkiö</a>
    </li>
    <li>
    <a href="https://matklad.github.io/2024/03/22/basic-things.html">Basic Things</a>, (Alex "matklad" Kladov includes Nyrkiö in his list of basic tooling every software project should use)
    </li>
    </ul>
    </>
    );
};


