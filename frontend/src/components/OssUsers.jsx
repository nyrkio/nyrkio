import { Swiper, SwiperSlide } from "swiper/react";
import { Navigation, Pagination } from "swiper/modules";

import 'swiper/css';
import 'swiper/css/navigation';
import 'swiper/css/pagination';
import '../style/components/swiper.scss';
import {Icon} from "./Icon.jsx";

const companies = [
  {
    title: "MongoDB",
    description: [
      "The MongoDB performance team is the home of this idea, and the core math behind the E-Divisive Means algorithm was implemented there.",
      "After almost a decade in production use, the shift to Continuous Benchmarking has unlocked a culture where responsibility for performance benchmarks and fixing regressions has been delegated to individual feature teams. Nowadays MongoDB automatically analyzes over a million data points per build, produced by their automated performance testing framework.",
    ],
    links: [
      {
        title: "Change Point Detection in Software Performance Testing",
        url: "https://arxiv.org/abs/2003.00584",
        meta: "Daly et al., 2020",
      },
      {
        title: "Automated System Performance Testing at MongoDB",
        url: "https://arxiv.org/abs/2004.08425",
        meta: "Ingo & Daly, 2020",
      },
      {
        title: "Creating a Virtuous Cycle in Performance Testing at MongoDB",
        url: "https://dl.acm.org/doi/10.1145/3427921.3450234",
        meta: "Daly, 2021",
      },
      {
        title: "MongoDB 8.0: Improving Performance, Avoiding Regressions",
        url: "https://www.mongodb.com/company/blog/mongodb-8-0-improving-performance-avoiding-regressions",
        meta: "Mark Benvenuto, 2025",
      },
    ],
  },

  {
    title: "Netflix",
    description: [
      "At Netflix, maintaining reliable performance is paramount to the end-user experience.",
      "The Netflix TVUI team was the first company to use the Change Point Detection algorithm developed and open-sourced at MongoDB.",
    ],
    links: [
      {
        title: "Fixing Performance Regressions Before They Happen",
        url: "https://netflixtechblog.com/fixing-performance-regressions-before-they-happen-eab2602b86fe",
        meta: "Angus Croll, 2022",
      },
      {
        title: "Netflix: A Shining Example of QA Done Right",
        url: "https://bismabhundi.medium.com/netflix-a-shining-example-of-qa-done-right-c566196dfceb",
        meta: "Bisma Latif, 2024",
      },
    ],
  },

  {
    title: "DataStax",
    description: [
      "DataStax automated a suite of performance tests as part of a Continuous Benchmarking workflow.",
      "DataStax built upon the E-Divisive algorithm open-sourced by MongoDB and transformed it into a fully functional command-line tool.",
    ],
    links: [
      {
        title:
          "Hunter: Using Change Point Detection to Hunt for Performance Regressions",
        url: "https://arxiv.org/abs/2301.03034",
        meta: "Fleming & Kołaczkowski, 2024",
      },
      {
        title: "Detecting Performance Regressions with DataStax Hunter",
        url: "https://medium.com/building-the-open-data-stack/detecting-performance-regressions-with-datastax-hunter-c22dc444aea4",
        meta: "Piotr Kołaczkowski",
      },
    ],
  },

  {
    title: "Confluent",
    description: [
      "Confluent uses Apache Otava as part of a Continuous Benchmarking workflow to test Kafka Streams performance.",
    ],
    links: [
      {
        title:
          "Automating Speed: A Proven Approach to Preventing Performance Regressions in Kafka Streams",
        url: "https://www.confluent.io/events/kafka-summit-london-2024/automating-speed-a-proven-approach-to-preventing-performance-regressions-in/",
        meta: "Alexander Sorokoumov & John Roessler, 2024",
      },
    ],
  },

  {
    title: "Red Hat OpenShift",
    description: [
      "OpenShift is Red Hat's Kubernetes platform.",
      "Red Hat uses Apache Otava as part of Cloud Bulldozer, a performance testing and analysis framework.",
    ],
    links: [
      {
        title: "Cloud Bulldozer",
        url: "https://github.com/cloud-bulldozer",
        meta: "GitHub",
      },
    ],
  },

  {
    title: "Tarantool",
    description: [
      "Tarantool is a NoSQL database and Lua application server known for high performance.",
      "To guard against performance regressions, they recently added Apache Otava to their CI pipeline.",
    ],
    links: [
      {
        title: "Project discussion about Apache Otava",
        url: "https://github.com/tarantool/tarantool/pull/11408",
        meta: "GitHub",
      },
    ],
  },
];

const CompanyCard = ({ item }) => {
  return (
    <div className="h-100 p-4 d-flex flex-column border rounded-2 bg-white shadow-sm border border-primary">
      <h3 className="mb-3 fs-5 ff-base text-center text-secondary ls-0">{item.title}</h3>

      {item.description.map((text, index) => (
        <p key={index}>{text}</p>
      ))}
      <br/>
      <ul className="ps-3 mt-auto mb-0">
        {item.links.map((link, index) => (
          <li key={index} className="mb-2">
            <a
              href={link.url}
              target="_blank"
              rel="noopener noreferrer"
            >
              {link.title}
            </a>
            {link.meta && <> — {link.meta}</>}
          </li>
        ))}
      </ul>
    </div>
  );
};

export const OssUserSlider = () => {
  return (
    <div className="swiper-slider">
      <button type="button" className="btn btn-swiper btn-prev btn-primary btn-square d-none d-xl-block" id="oss-users-prev" aria-label="Previous">
        <Icon name="chevron-left" size={24} className="text-white"/>
      </button>
      <button type="button" className="btn btn-swiper btn-next btn-primary btn-square d-none d-xl-block" id="oss-users-next" aria-label="Next">
        <Icon name="chevron-right" size={24} className="text-white"/>
      </button>
      <Swiper
        modules={[Pagination, Navigation]}
        spaceBetween={20}
        pagination={{ clickable: true }}
        autoHeight={true}
        navigation={{
          prevEl: '#oss-users-prev',
          nextEl: '#oss-users-next',
        }}
        slidesPerView={1}
        breakpoints={{
          768: {
            slidesPerView: 2,
            autoHeight: false,
          },

          992: {
            slidesPerView: 3,
            autoHeight: false,
          },

          1400: {
            slidesPerView: 4,
            autoHeight: false,
          },
        }}
      >
        {companies.map((item, index) => (
          <SwiperSlide key={index} className="h-auto">
            <CompanyCard item={item} />
          </SwiperSlide>
        ))}
      </Swiper>
    </div>
  );
};
