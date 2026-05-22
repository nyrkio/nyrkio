import { Slogan } from "../Logo.jsx";
import './HeroBanner.scss';
import heroBannerChart from "../../static/hero-banner-chart.webp";


export const HeroBanner = ({ cta }) => {

  return (
    <div className="hero-banner">
      <img
        className="hero-banner__background"
        src='/p/NyyrikkiRunner/RunnerSquirrelBackground-ytbanner6-2880.jpg'
        alt="Hero banner"
        width="2880"
        height="1348"
        loading="eager"
      />

      <div className="hero-banner__content w-100">
        <div className="container text-center">
          <h1 className="hero-banner__slogan">
            <Slogan text={true}/>
          </h1>
        </div>
        <div className="container-fluid">
          <div className="row flex-column align-items-center flex-xl-row">
            <div className="col-12 col-xl-4 col-xxl-5 d-none d-xl-block">
            </div>
            <div className="col-12 col-xl-4 col-xxl-5 p-4 ps-xxl-7 pe-xl-6 order-xl-2">
              <img className="hero-banner__image ms-auto" src={heroBannerChart} alt="Hero chart" width="1218" height="514"/>
            </div>
            <div className="col-12 col-xl-4 col-xxl-2">
              {cta?.access && cta?.url && (
                <div className="hero-banner__cta text-center">
                  <a className="btn btn-primary text-nowrap" href={cta.url}>
                    <span dangerouslySetInnerHTML={{__html: cta.title}}/>
                  </a>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
