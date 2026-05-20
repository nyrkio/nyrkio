import ToS from "../static/doc/Nyrkio Terms of Service v2 - 2026-02-19.pdf";
import PrivacyPolicy from "../static/doc/Privacy Policy Nyrkiö 2024 v1.0.pdf";
import {Link} from "react-router-dom";
import footerUpperCrust from "../static/footer-white-graphic.png";
import {RssWidget} from "./RssWidget/RssWidget.jsx";
import backgroundImg from "../static/Sayhteella.jpg";
import '../style/components/footer-banner.scss'
import { SmallLogo } from "./Logo";
import icon from "./Icon.jsx";
import Icon from "./Icon.jsx";

export const Footer = () => {
  return (<>

    <RssWidget />
    <footer className="">
      <div className="footer-banner py-section">
        <div className="container">
          <div className="footer-banner__copyright p-3 p-md-4 rounded-3 shadow bg-white">
            <a className="d-inline-block mb-3 mb-md-4" href="/frontpage">
              <SmallLogo loading={'lazy'} />
            </a>
            <p>
              Nyrkiö Change Detection Service is based on the open source Apache Otava (Incubating) project. <br/>
              Apache and Apache Otava are trademarks of
              the <br/><a href="https://apache.org">Apache Software Foundation</a>.
            </p>
            <p>
              @nyrkio/change-detection GitHub action is based on the <a
              href="https://github.com/benchmark-action/github-action-benchmark">Github-Action-Benchmark project</a>.
            </p>
            <p>
              Nyrkiö GitHub runners use the Ec2 image from <a href="https://runs-on.com">Runs-on.com</a>. Thank you for making those available!
              <br/>
              GitHub and the Octocat 2.0 mascot (Mona) are trademarks of GitHub Inc.
              <br/>
              The watercolor picture with Nyyrikki and Mona running is &copy; Ebba Ingo, 2026.
            </p>

            <nav className="d-flex gap-3 justify-content-center mt-4">
              <a target="_blank" href="https://github.com/nyrkio/nyrkio" aria-label="Github">
                <Icon name="github-circle" size={32}/>
              </a>
              <a target="_blank" href="https://twitter.com/nyrkio" aria-label="Twitter">
                <Icon name="twitter-circle" size={32}/>
              </a>
              <a target="_blank" href="https://www.youtube.com/@Nyrkio" aria-label="Youtube">
                <Icon name="youtube-circle" size={32} className="text-primary"/>
              </a>
              <a target="_blank" href="https://www.instagram.com/nyrk.io/" aria-label="Instagram">
                <Icon name="instagram-circle" size={32}/>
              </a>
              <a target="_blank" href="https://www.tiktok.com/@nyrk.io" aria-label="TikTok">
                <Icon name="tiktok-circle" size={32}/>
              </a>
            </nav>
          </div>
        </div>


        <div className="footer-banner__background">
          <img
            className="img-fluid "
            src="/p/NyyrikkiRunner/RunnerSquirrelBackground-ytbanner6-2880.jpg"
            alt="Footer banner"
            width="2880"
            height="1348"
            loading="lazy"
          />
        </div>
      </div>
      <div className="container py-3 py-md-4">
        <div className="row">
          <div className="col-6 col-md-4">
            <Link className="link-secondary link-underline-opacity-0 link-underline-opacity-100-hover" to={ToS}
                  target="_blank" aria-label="View Terms of Service PDF">Terms of Service</Link>
          </div>
          <div className="col-12 col-md-4 order-last order-md-0 text-center mt-3  mt-md-0">
            <div className="d-inline-flex align-items-center">
              <Icon name="copyright" size={24} className="text-body icon-copyright"/>
              &nbsp;
              {new Date().getFullYear()} Nyrkiö Oy.
            </div>
          </div>
          <div className="col-6 col-md-4 text-end">
            <Link className="link-secondary link-underline-opacity-0 link-underline-opacity-100-hover"
                  to={PrivacyPolicy} target="_blank" aria-label="View Privacy Policy PDF">Privacy Policy</Link>
          </div>
        </div>
      </div>
    </footer>
  </>)
};

