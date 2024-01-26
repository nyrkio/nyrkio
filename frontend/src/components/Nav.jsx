import { LogOut, LoginButton } from "./Login.jsx";
import { UserMenu } from "./UserMenu.jsx";

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
          <li className="nav-item">
            <a className="nav-link" href="#">
              Company
            </a>
          </li>
          <li className="nav-item">
            <a className="nav-link" href="#">
              Product
            </a>
          </li>
          <li className="nav-item">
            <a className="nav-link" href="#">
              Pricing
            </a>
          </li>
          <li className="nav-item">
            <a className="nav-link" href="#">
              Services
            </a>
          </li>
          <li className="nav-item">
            <a className="nav-link" href="#">
              Research
            </a>
          </li>
          <li className="nav-item">
            <a className="nav-link" href="/docs/getting-started">
              Docs
            </a>
          </li>
        </ul>
      </div>
    </>
  );
};

export const NavHeader = ({ loggedIn, setLoggedIn }) => {
  return (
    <nav className="navbar navbar-expand-lg navbar-top">
      <div className="container-fluid">
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
