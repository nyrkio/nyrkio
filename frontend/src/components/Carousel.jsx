import Carousel from 'react-bootstrap/Carousel';
import Pekka from '../static/ScreenshotTwitterPekkaEnberg.png';
import Joran from '../static/Screenshot_Joran_Dirk_Greef.png';
import Pierre from '../static/Pierre_lake.jpg';
import { DemoVideo } from './FrontPage'

function NyrkioCarousel() {
  return (
    <Carousel interval={10*1000}>
      <Carousel.Item>
        <DemoVideo />
      </Carousel.Item>
      <Carousel.Item>
        <img src={Pekka} className="w-50" />
        <Carousel.Caption>
        <p><em>Pekka Enberg, Founder &amp; CTO, Turso</em></p>
        </Carousel.Caption>
      </Carousel.Item>
      <Carousel.Item>
        <img src={Joran} className="w-50" />
        <Carousel.Caption>
        <p><em>Joran Dirk Greef, CEO of Tigerbeetle</em></p>
        </Carousel.Caption>
      </Carousel.Item>
      <Carousel.Item>
        <img src={Pierre} className="" />
        <Carousel.Caption className="pierre">
        <p className="pierre"><em>Pierre Laporte,
        Senior Staff Software Engineer, Dremio</em></p>
        </Carousel.Caption>
      </Carousel.Item>
    </Carousel>
  );
}

export default NyrkioCarousel;
