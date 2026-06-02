import { useEffect, useState } from "react";
import * as rssParser from 'react-native-rss-parser';
import { Swiper, SwiperSlide } from "swiper/react";
import { Navigation, Pagination } from "swiper/modules";
import './RssWidget.scss';


export const RssWidget = () => {
  const [rssFeed, setRssFeed] = useState([]);
  const readRss = async () => {
    return fetch('https://blog.nyrkio.com/feed')
      .then((response) => response.text())
      .then((responseData) => rssParser.parse(responseData))
      .then((rss) => {
        setRssFeed(rss.items);
      });
  };

  const [loading, setLoading] = useState(true);
  useEffect(()=>{
    setLoading(true);
    readRss()
    .then(()=>{console.log("done");})
    .catch((err)=>{console.error(err);})
    .finally(()=>setLoading(false));
  },[]);

  const RssListItems = ({ feed }) => {
    return (
      <div className="swiper-slider">
        <Swiper
          className="swiper--rss-list"
          modules={[Navigation, Pagination]}
          spaceBetween={20}
          slidesPerView={3}
          navigation
          pagination={{ clickable: true }}
          breakpoints={{
            0: { slidesPerView: 1 },
            768: { slidesPerView: 2 },
            1024: { slidesPerView: 3 },
          }}
        >
          {feed.slice(0, 3).map((item) => {
            const d = new Date(Date.parse(item.published));

            return (
              <SwiperSlide key={item.id}>
                <div className="rss-card d-flex flex-column shadow-sm rounded-3 border border-primary p-3 h-100">
                  <div className="rss-card__image rounded-3 ratio ratio-16x9 mb-4 overflow-hidden" style={{backgroundColor: '#D9D9D9'}}>
                    {/* @todo: add image <img className="img-fluid w-100" src={item.image} alt={`${item.title} teaser`} loading="lazy"/>*/}
                  </div>
                  <h3 className="rss-card__title text-secondary h5">{item.title}</h3>
                  <div className="rss-card__footer d-flex justify-content-between mt-auto">
                    <div className="rss-card__author text-truncate">{item.authors?.[0]?.name || "Unknown"}</div>
                    <div className="rss-card__date">
                      {new Intl.DateTimeFormat("en-US", {
                        year: "numeric",
                        month: "long",
                        day: "numeric",
                      }).format(d)}
                    </div>
                  </div>
                  <a className="rss-card__link" href={item.links?.[0]?.url} target="_blank" rel="noopener noreferrer">{item.title}</a>
                </div>
              </SwiperSlide>
            );
          })}
        </Swiper>
      </div>
    );
  };

  return (
    <>
      <section className="my-section container">
        <h2 className="text-center text-primary mb-5">Recently on blog</h2>
        {loading ? "" : (<RssListItems feed={rssFeed} />)}
        <div className="text-center mt-3 mt-lg-5">
          <a className="btn btn-outline-primary d-block d-md-inline-block" href="https://blog.nyrkio.com/" target="_blank" rel="noopener noreferrer">View all articles</a>
        </div>
      </section>
    </>
  );
};
