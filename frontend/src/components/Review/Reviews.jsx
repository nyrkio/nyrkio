import { Swiper, SwiperSlide } from 'swiper/react';
import { Navigation, Pagination } from 'swiper/modules';
import './Reviews.scss';
import 'swiper/css';
import 'swiper/css/navigation';
import 'swiper/css/pagination';
import '../../style/components/swiper.scss';

import { companiesData } from './../UsersPage.jsx';
import ReviewCard from '../ReviewCard/ReviewCard.jsx';
import Icon from "../Icon.jsx";

export default function UsersReviewsSection() {
  const companies = Object.values(companiesData);

  return (
    <section className="my-section container section--reviews">
      <h2 className="text-center text-primary mb-5">
        What our users say
      </h2>

      <div className="my-4">
        <div className="swiper-slider swiper--reviews">
          <button type="button" className="btn btn-swiper btn-prev btn-primary btn-square d-none d-xl-block" id="reviews-prev" aria-label="Previous">
            <Icon name="chevron-left" size={24} className="text-white"/>
          </button>
          <button type="button" className="btn btn-swiper btn-next btn-primary btn-square d-none d-xl-block" id="reviews-next" aria-label="Next">
            <Icon name="chevron-right" size={24} className="text-white"/>
          </button>
          <Swiper
            modules={[Navigation, Pagination]}
            spaceBetween={20}
            slidesPerView={3}
            navigation={{
              prevEl: '#reviews-prev',
              nextEl: '#reviews-next',
            }}
            pagination={{ clickable: true }}
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
            {companies.map((company) => (
              <SwiperSlide key={company.quoteData.author.name}>
                <ReviewCard
                  quoteData={company.quoteData}
                  logo={company.logo}
                />
              </SwiperSlide>
            ))}
          </Swiper>
        </div>

      </div>

      <div className="text-center">
        <a className="btn btn-outline-primary" href="/product/user-testimonials">See all reviews</a>
      </div>
    </section>
  );
}
