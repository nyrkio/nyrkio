import Carousel from 'react-bootstrap/Carousel';
import Pekka from '../static/ScreenshotTwitterPekkaEnberg.png';
import Joran from '../static/Screenshot_Joran_Dirk_Greef.png';
import Pierre from '../static/Pierre_lake.jpg';
import { DemoVideo } from './FrontPage'
import Marketplace_GHA from '../static/Nyrkio-GHA-Marketplace-Listing.png'

export function NyrkioCarousel() {
  return (
    <Carousel interval={7*1000}>
    <Carousel.Item  interval={15*1000}>
        <a href="/docs/getting-started">
        <img src={Marketplace_GHA} className="w-50" />
        </a>
        <Carousel.Caption>
        <div style={{"width":"20em", "position":"absolute", "left": "55%", "bottom":"0px", "textAlign":"left"}}>
        <p><a href="/docs/getting-started"><strong>NEW: </strong><br /> Adding Nyrkiö Change Detection to your GitHub .workflows just got easy!</a></p>
        <ol>
        <li><a href="/docs/getting-started">Install Nyrkiö as GitHub app.</a></li>
        <li><a href="/docs/getting-started">Add 10 lines of Yaml</a></li>
        <li><a href="/docs/getting-started">Remember to pass the JWT token.</a></li>
        </ol>
        <p><a href="/docs/getting-started">That's all.</a></p>
        </div>
        </Carousel.Caption>
      </Carousel.Item>
      <Carousel.Item>
        <DemoVideo />
      </Carousel.Item>
    </Carousel>
  );
}

export function UserCarousel() {
  return (
    <Carousel interval={7*1000}>
    <Carousel.Item interval={5*1000}>
    <img src={Pekka} className="w-50" />
    <Carousel.Caption>
    <p><em><a href="https://nyrkio.com/public/https%3A%2F%2Fgithub.com%2Ftursodatabase%2Flimbo/main">Pekka Enberg, Founder &amp; CTO, Turso<br /> View Limbo benchmark results...</a></em></p>
    </Carousel.Caption>
    </Carousel.Item>
    <Carousel.Item>
    <img src={Joran} className="w-50" />
    <Carousel.Caption>
    <p><em><a href="https://nyrkio.com/public/https%3A%2F%2Fgithub.com%2Ftigerbeetle%2Ftigerbeetle/main/devhub">Joran Dirk Greef, CEO of Tigerbeetle<br />View Tigerbeetle benchmark results... </a></em></p>
    </Carousel.Caption>
    </Carousel.Item>
    <Carousel.Item>
    <img src={Pierre} className="" />
    <Carousel.Caption className="pierre">
    <p className="pierre"><em><a href="https://blog.nyrkio.com/2025/03/25/interview-with-pierre-laporte-part-i/">Pierre Laporte,
    Senior Staff Software Engineer, Dremio<br />Read more...</a></em></p>
    </Carousel.Caption>
    </Carousel.Item>
    </Carousel>
  );
}

export default NyrkioCarousel;
