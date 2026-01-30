import { LogOut, LoginButton } from "./Login.jsx";
import { UserMenu } from "./UserMenu.jsx";
import { SmallLogo } from "./Logo";
import { ImpersonateControls } from "./ImpersonateControls";

const NavigationItems = () => {
  return (
    <>
        <ul className="navbar-nav me-auto mb-2 mb-lg-0">
          <li className="nav-item nyrkio-logo-nav-item">
            <a
              className="nav-link nyrkio-logo-nav-link"
              aria-current="page"
              href="/frontpage"
              title="frontpage"
            >
              <SmallLogo />
            </a>
          </li>
          <li className="nav-item">
          <a className="nav-link" href="/dash">
          Dashboards
          </a>
          </li>
          <li className="nav-item">
          <a className="nav-link" href="/product">
          Product
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
          <li className="nav-item">
            <a className="nav-link" href="https://blog.nyrkio.com" title="Blog">
              Blog
            </a>
          </li>
        </ul>
    </>
  );
};

export const NavHeader = ({ loggedIn, setLoggedIn }) => {
  return (
    <nav className="navbar navbar-light navbar-expand-md navbar-top">
      <div className="container-fluid m-1">
        <NavigationItems />
        {loggedIn ? (
            <UserMenu setLoggedIn={setLoggedIn} />
        ) : (
          <LoginButton />
        )}
        <div className=" nyrkio-login-controls">
        <ImpersonateControls />
        </div>
      </div>
    </nav>
  );
};

