import { LogOut, LoginButton } from "./Login.jsx";
import { UserMenu } from "./UserMenu.jsx";
import { SmallLogo } from "./Logo";

const NavigationItems = () => {
  return (
    <>
      <button
        className="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarSupportedContent"
        aria-controls="navbarSupportedContent"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span className="navbar-toggler-icon"></span>
      </button>
      <div className="collapse navbar-collapse" id="navbarSupportedContent">
        <ul className="navbar-nav me-auto mb-2 mb-lg-0">
          <li className="nav-item nyrkio-logo-nav-item">
            <a
              className="nav-link nyrkio-logo-nav-link"
              aria-current="page"
              href="/"
              title="Dashboards"
            >
              <SmallLogo />
            </a>
          </li>
          <li className="nav-item">
            <a className="nav-link" href="/product">
              Product
            </a>
          </li>
          <li className="nav-item">
            <a className="nav-link" href="/services">
              Services
            </a>
          </li>
          <li className="nav-item">
            <a className="nav-link" href="/docs/getting-started">
              Docs
            </a>
          </li>
          <li className="nav-item">
            <a className="nav-link" href="/about" title="About Nyrkiö">
              About
            </a>
          </li>
        </ul>
      </div>
    </>
  );
};

export const NavHeader = ({ loggedIn, setLoggedIn }) => {
  return (
    <nav className="navbar navbar-light navbar-expand-sm navbar-top">
      <div className="container-fluid m-1">
        <NavigationItems />
        {loggedIn ? (
          <>
            <UserMenu setLoggedIn={setLoggedIn} />
          </>
        ) : (
          <LoginButton />
        )}
      </div>
    </nav>
  );
};
