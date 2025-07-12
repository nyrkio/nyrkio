import Carousel from 'react-bootstrap/Carousel';
import { TursoMini, DremioMini, TigerbeetleMini } from "./UsersPage.jsx";
import Pekka from '../static/ScreenshotTwitterPekkaEnberg.png';
import Joran from '../static/Screenshot_Joran_Dirk_Greef.png';
import Pierre from '../static/Pierre_lake.jpg';
import { DemoVideo } from './FrontPage'
import Marketplace_GHA from '../static/Nyrkio-GHA-Marketplace-Listing.png'
import { useEffect, useState } from "react";


export function NyrkioCarouselCols() {
  return (
    <div className="row">
    <div className="col p-5">
    <a href="/docs/getting-started">
    <img src={Marketplace_GHA} className="w-100" />
    </a>
    <div>

    <div className="carousel-gha">
    <p><a href="/docs/getting-started"><strong>NEW: </strong><br />Adding Nyrkiö Change Detection to your GitHub .workflows just got easy!</a></p>
    <ol>
    <li><a href="/docs/getting-started">Install Nyrkiö as GitHub app.</a></li>
    <li><a href="/docs/getting-started">Add 10 lines of Yaml</a></li>
    <li><a href="/docs/getting-started">Remember to pass the JWT token.</a></li>
    </ol>
    <p><a href="/docs/getting-started">That's all.</a></p>
    </div>
    </div>
    </div>
    <div className="col p-5">
    <DemoVideo />
    </div>
    </div>
  );
}

export function NyrkioCarousel() {
  return (
    <Carousel interval={10*1000} slide={1500}>
      <Carousel.Item>
        <a href="/docs/getting-started">
        <img src={Marketplace_GHA} className="w-50" />
        </a>
        <Carousel.Caption>
        <div className="carousel-gha">
        <p><a href="/docs/getting-started"><strong>NEW: </strong><br /> Adding Nyrkiö Change Detection to your GitHub .workflows just got easy!</a></p>
        <ol>
          <li><a href="/docs/getting-started">Install Nyrkiö as GitHub app.</a></li>
          <li><a href="/docs/getting-started">Add 10 lines of Yaml</a></li>
          <li><a href="/docs/getting-started">Remember to pass the JWT token.</a></li>
        </ol>
        <p><a href="/docs/getting-started">Get started right away...</a></p>
        </div>
        </Carousel.Caption>
      </Carousel.Item>
      <Carousel.Item>
      <DemoVideo />
      <p className="mt-5"><a href="https://www.youtube.com/embed/EKAhgrdERfk?si=btV2C2wpDx4d-6lZ">▶ Nyrkiö introduction (YouTube)</a></p>
      </Carousel.Item>
    </Carousel>
  );
}

export function UserCarousel() {
    const [loading, setLoading] =useState(true);
    const [currentCarouselCard, setCurrentCarouselCard] = useState("Turso");

    const setT = () => {
      window.setTimeout(()=>{setLoading(false);next();setT()}, 30000);
    }
    // By definition: [] is at end of loading
    useEffect(()=>{setLoading(false); setT()},[]);

    const next = () => {
      console.log("next",loading);
      if(loading) return;
      if (currentCarouselCard == "Turso"){
        setLoading(true);
        setCurrentCarouselCard("Dremio")
      }
      if (currentCarouselCard == "Dremio"){
        setLoading(true);
        setCurrentCarouselCard("Tigerbeetle")
      }
      if (currentCarouselCard == "Tigerbeetle"){
        setLoading(true);
        setCurrentCarouselCard("Turso")
      }

    };
    const prev = () => {
      if(loading) return;

      if (currentCarouselCard == "Turso"){
        setLoading(true);
        setCurrentCarouselCard("Tigerbeetle")
      }
      if (currentCarouselCard == "Tigerbeetle"){
        setLoading(true);
        setCurrentCarouselCard("Dremio")
      }
      if (currentCarouselCard == "Dremio"){
        setLoading(true);
        setCurrentCarouselCard("Turso")
      }
    };


  if (currentCarouselCard == "Turso") {
    return (
      <div className="row">
      <div style={{position: "absolute", left: "0px", height: "100%", width: "25%", cursor: "pointer"}} onClick={()=>{setLoading(false);prev();}}></div>
      <TigerbeetleMini addClassName="carousel-postview"  onClick={prev()}/>
      <TursoMini />
      <DremioMini addClassName="carousel-preview" onClick={next()}/>
      <div style={{position: "absolute", right: "0px", height: "100%", width: "25%", cursor: "pointer"}} onClick={()=>{setLoading(false);next();}}></div>
      </div>
    );
  }
  if (currentCarouselCard == "Dremio") {
    return (
      <div className="row">
      <div style={{position: "absolute", left: "0px", height: "100%", width: "25%", cursor: "pointer"}} onClick={()=>{setLoading(false);prev();}}></div>
      <TursoMini addClassName="carousel-postview"  onClick={prev()} />
      <DremioMini />
      <TigerbeetleMini addClassName="carousel-preview"  onClick={next()} />
      <div style={{position: "absolute", right: "0px", height: "100%", width: "25%", cursor: "pointer"}} onClick={()=>{setLoading(false);next();}}></div>
      </div>
    );
  }
  if (currentCarouselCard == "Tigerbeetle") {
    return (
      <div className="row">
      <div style={{position: "absolute", left: "0px", height: "100%", width: "25%", cursor: "pointer"}} onClick={()=>{setLoading(false);prev();}}></div>
      <DremioMini addClassName="carousel-postview"  onClick={prev()} />
      <TigerbeetleMini />
      <TursoMini addClassName="carousel-preview"  onClick={next()} />
      <div style={{position: "absolute", right: "0px", height: "100%", width: "25%", cursor: "pointer"}} onClick={()=>{setLoading(false);next();}}></div>
      </div>
    );
  }
  return (<></>);
}

export default NyrkioCarousel;
