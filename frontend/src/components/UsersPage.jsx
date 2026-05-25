import tursoLogo from "../static/turso-banner.png";
import tursoPekka from "../static/people/PekkaEnberg-600x800.jpg";
import dremioLogo from "../static/dremio_logo.png";
import dremioPierre from "../static/people/Pierre-Dog-600x800.jpg";
import kiekerLogo from "../static/kieker-logo.svg";
import kiekerYang from "../static/people/ShinhyungYang-600x800.jpg";
import tigerbeetleLogo from "../static/tb-logo-black.png";
import tigerbeetleJoran from "../static/people/Joran-600x800.jpg";

import {Icon} from "./Icon.jsx";
import {Swiper, SwiperSlide} from "swiper/react";
import {Navigation} from "swiper/modules";
import {ReviewCard} from "./ReviewCard/ReviewCard.jsx";
import { WhatMore } from "./WhatMore/WhatMore.jsx";
import 'swiper/css';
import 'swiper/css/navigation';
import 'swiper/css/pagination';
import '../style/components/swiper.scss';

export const companiesData = {
  turso: {
    logo: {
      src: tursoLogo,
      alt: 'Turso logo',
      width: 1916,
      height: 1080,
    },
    label: 'Turso',
    description: 'Turso Database is an active open source project that is rewriting good old SQLite in Rust. With over 200 contributors each month, this project is merging a dozen patches each day. To move fast with confidence they need airthight test coverage also for performance. TPC-H, Clickbench and various self made test queries run after each merge. The company behind the open source project is also operating a Database as a Service.',
    links: [
      '<a href="/public/https%3A%2F%2Fgithub.com%2Ftursodatabase%2Flimbo/main/">Public Test Result</a>',
      '<a href="https://www.youtube.com/watch?v=iiS0KoYc_Zc" target="_blank">Video</a>',
    ],
    quoteData: {
      author: {
        image: {
          src: tursoPekka,
          alt: 'Pekka Enberg photo',
          width: 600,
          height: 800,
        },
        name: 'Pekka Enberg',
        position: 'Founder',
        company: 'Turso Database',
      },
      text: 'Good news is we finally have Nyrkiö configured for Turso. And it detects our improvements too! Bad news is that we [didn\'t do it sooner...]',
      link: '<a href="/public/https%3A%2F%2Fgithub.com%2Ftursodatabase%2Flimbo/main/">Public Test Result</a>'
    }
  },
  dremio: {
    logo: {
      src: dremioLogo,
      alt: 'Dremio logo',
      width: 512,
      height: 256,
    },
    label: 'Dremio',
    description: 'Dremio develops and sells Big Data solutions based on Apache Iceberg. To ensure that there aren\'t any performance regressions, a TPC-H benchmark is run weekly. Dremio were one of the first users to try Nyrkio the very same day we launched, and when testing Nyrkiö with some old benchmark results, Nyrkiö was able to find a regression the team had not noticed before!',
    links: [
      '<a href="https://blog.nyrkio.com/2025/03/25/interview-with-pierre-laporte-part-i/" target="_blank">Interview (part 1)</a>',
      '<a href="https://blog.nyrkio.com/2025/03/31/interview-with-pierre-laporte-part-2/" target="_blank">Interview (part 2)</a>',
    ],
    quoteData: {
      author: {
        image: {
          src: dremioPierre,
          alt: 'Pierre Laporte photo',
          width: 600,
          height: 800,
        },
        name: 'Pierre Laporte',
        position: 'Senior Staff Performance Engineer',
        company: 'Dremio',
      },
      text: 'Nyrkiö is able to detect change points even in high-variance data. So that solved the first challenge entirely. We could focus on reducing the variance with the piece of mind that detection was a solved problem.',
      link: '<a href="https://blog.nyrkio.com/2025/03/25/interview-with-pierre-laporte-part-i/" target="_blank">Interview (part 1)</a>',
    }
  },
  tigerbeetle: {
    logo: {
      src: tigerbeetleLogo,
      alt: 'Tigerbeetle logo',
      width: 1920,
      height: 461,
    },
    label: 'Tigerbeetle',
    description: 'TigerBeetle is a specialized transactions database, designed for safety and 1000x performance, to power the future of online transaction processing (OLTP). The architecture is based on the realization that batching multiple transactions into one large commit can achieve much faster velocity than a traditional general purpose database. A notable property in Tigerbeetle\'s use of Nyrkiö: they track 100% percentile latency (so max latency) and variation in this is considered a regression!',
    links: [
      '<a href="https://nyrkio.com/public/https%3A%2F%2Fgithub.com%2Ftigerbeetle%2Ftigerbeetle/main/devhub">Public Test Result</a>',
      '<a href="https://matklad.github.io/2024/03/22/basic-things.html" target="_blank">Basic Things</a>',
    ],
    quoteData: {
      author: {
        image: {
          src: tigerbeetleJoran,
          alt: 'Joran Dirk Greef photo',
          width: 600,
          height: 800,
        },
        name: 'Joran Dirk Greef',
        position: 'Founder & CEO',
        company: 'Tigerbeetle',
      },
      text: 'Nyrkiö did a better job than our internal graphs.',
      link: '<a href="https://nyrkio.com/public/https%3A%2F%2Fgithub.com%2Ftigerbeetle%2Ftigerbeetle/main/devhub">Public Test Result</a>',
    }
  },
  kieker: {
    logo: {
      src: kiekerLogo,
      alt: 'Kieker logo',
      width: 494,
      height: 150,
    },
    label: 'Kieker',
    description: 'Kieker is a research project by Computer Science Department of Kiel University (et.al.). The project has long traditions in the area of software performance, going back to the very beginnings of the <a href="https://icpe.spec.org/">ICPE community</a> in 2009-2012.<br>They produce a framework for monitoring and instrumenting your software development projects. An interesting sub-project is that they constantly monitor the overhead incurred by their own monitoring framework, and other frameworks. As a by-product, they end up producing a valuable service to the entire GitHub community: Their dashboard effectively monitors the performance variations in the standard GitHub Actions test runners.',
    links: [
      '<a href="https://nyrkio.com/public/https%3A%2F%2Fgithub.com%2Fshinhyungyang%2Fmoobench/main/Kieker-java">Public Test Result</a>',
      '<a href="https://arxiv.org/abs/2510.11310" target="_blank">Joint Research Article</a>',
      '<a href="https://kieker-monitoring.net/" target="_blank">Kieker</a>',
    ],
    quoteData: {
      author: {
        image: {
          src: kiekerYang,
          alt: 'Dr Shinhyung Yang photo',
          width: 600,
          height: 800,
        },
        name: 'Dr Shinhyung Yang',
        position: 'Kiel University',
      },
      text: 'We use Nyrkiö as an implementation of the E-Divisive Change Point Detection algorithm in parallel with our own monitoring dashboard. This provides independent validation of our own findings. We also like that the graphs look prettier than our own!',
      link: '<a href="https://nyrkio.com/public/https%3A%2F%2Fgithub.com%2Fshinhyungyang%2Fmoobench/main/Kieker-java" target="_blank">Kieker</a>',
    },
  }
}

export const UsersPage = () => {
  return (<>
    <div className="container mb-section mt-4 mt-md-6">
      <h1 className="text-center text-primary mb-4 mb-md-5">What Nyrkiö users are saying</h1>

      <div className="swiper-slider swiper--reviews">
        <button type="button" className="btn btn-swiper btn-prev btn-primary btn-square d-none d-xl-block" id="reviews-prev" aria-label="Previous">
          <Icon name="chevron-left" size={24} className="text-white"/>
        </button>
        <button type="button" className="btn btn-swiper btn-next btn-primary btn-square d-none d-xl-block" id="reviews-next" aria-label="Next">
          <Icon name="chevron-right" size={24} className="text-white"/>
        </button>
        <Swiper
          modules={[Navigation]}
          spaceBetween={20}
          slidesPerView={3}
          navigation={{
            prevEl: '#reviews-prev',
            nextEl: '#reviews-next',
          }}
          breakpoints={{
            0: {
              slidesPerView: 1,
            },
            768: {
              slidesPerView: 2,
            },
            1400: {
              slidesPerView: 3,
            },
          }}
        >
          {Object.entries(companiesData).map(([id, company]) => (
            <SwiperSlide key={id}>
              <ReviewCard
                company={company}
                variant="full"
              />
            </SwiperSlide>
          ))}
        </Swiper>
      </div>
    </div>

    <WhatMore />
  </>)
};
