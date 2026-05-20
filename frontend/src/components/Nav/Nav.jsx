import { Link } from "react-router-dom";
import { LogOut, LoginButton } from "./../Login.jsx";
import { UserMenu } from "./../UserMenu.jsx";
import { SmallLogo } from "./../Logo";
import { ImpersonateControls } from "./../ImpersonateControls";
import "./Nav.scss";
import Icon from "../Icon.jsx";

const NavigationItems = () => {
  return (
    <>
      <ul className="navbar-nav w-100 w-lg-auto me-lg-auto mb-5 mb-lg-0 gap-lg-4">
        <li className="nav-item">
          <a className="nav-link" href="/dash">Dashboards</a>
        </li>
        <li className="nav-item">
          <a className="nav-link" href="/product">Product</a>
        </li>
        <li className="nav-item">
          <a className="nav-link" href="/docs/getting-started">Docs</a>
        </li>
        <li className="nav-item">
          <a className="nav-link" href="/about">About</a>
        </li>
        <li className="nav-item">
          <a className="nav-link" href="https://blog.nyrkio.com">Blog</a>
        </li>
      </ul>
    </>
  );
};

export const NavHeader = ({ loggedIn, setLoggedIn }) => {
  return (
    <nav className="navbar navbar-site align-items-center navbar-light bg-white navbar-expand-lg navbar-top shadow px-3 py-3 my-4 rounded-2 gap-2 gap-xl-4">
      <a className="navbar-brand p-0" aria-current="page" href="/frontpage" title="frontpage">
        <SmallLogo/>
      </a>

      <button className="btn-none d-lg-none" type="button" data-bs-toggle="offcanvas" data-bs-target="#navbarMain" aria-controls="navbarMain" aria-label="Open Main menu">
        <Icon name="menu-burger" size={32}/>
      </button>
      <div className="offcanvas offcanvas-end offcanvas-lg" tabIndex="-1" id="navbarMain">
        <div className="offcanvas-header">
          <a className="navbar-brand p-0" aria-current="page" href="/frontpage" title="frontpage">
            <SmallLogo/>
          </a>
          <button type="button" className="btn-none ms-auto" data-bs-dismiss="offcanvas" aria-label="Close">
            <Icon name="close" size={24}/>
          </button>
        </div>
        <div className="offcanvas-body align-items-lg-center d-flex flex-column flex-lg-row">
            <NavigationItems/>
            {loggedIn ? (
              <UserMenu loggedIn={loggedIn} setLoggedIn={setLoggedIn}/>
            ) : (
              <div className="loginmenu d-flex gap-3 gap-xl-4 mt-auto mt-lg-0">
                <Link to="/signup" className="btn btn-outline-primary signupbutton w-100 w-lg-auto">
                  Create account
                </Link>
                <Link to="/login"  className="btn btn-primary loginbutton w-100 w-lg-auto">
                  Log In
                </Link>
              </div>
            )}
            <div className="nyrkio-login-controls">
              <ImpersonateControls/>
            </div>
          </div>
      </div>

    </nav>
  );
};

