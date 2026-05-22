import { Link, NavLink } from "react-router-dom";
import { useState } from "react";
import { Navbar, Container, Offcanvas, Nav } from "react-bootstrap";
import { LogOut, LoginButton } from "./../Login.jsx";
import { UserMenu } from "./../UserMenu.jsx";
import { SmallLogo } from "./../Logo";
import { ImpersonateControls } from "./../ImpersonateControls";
import "./Nav.scss";
import Icon from "../Icon.jsx";

const navLinkClass = ({ isActive }) =>
  `nav-link ${isActive ? "active" : ""}`;

export const NavHeader = ({ loggedIn, setLoggedIn }) => {
  const [showMenu, setShowMenu] = useState(false);

  const handleClose = () => setShowMenu(false);
  const handleShow = () => setShowMenu(true);

  return (
    <Navbar
      expand="lg"
      className="navbar-site align-items-center navbar-light bg-white navbar-top shadow px-3 py-3 my-4 rounded-2 gap-2 gap-xl-4"
    >
      <Container fluid className="p-0 d-flex justify-content-between align-items-center">

        <Navbar.Brand as={Link} to="/frontpage" className="p-0" title="frontpage">
          <SmallLogo/>
        </Navbar.Brand>

        <button
          className="btn-none d-lg-none"
          type="button"
          onClick={handleShow}
          aria-label="Open Main menu"
        >
          <Icon name="menu-burger" size={32}/>
        </button>

        <Navbar.Offcanvas
          id="navbarMain"
          placement="end"
          show={showMenu}
          onHide={handleClose}
          restoreFocus={false}
          className="offcanvas-lg navbar-site--offcanvas"
        >
          <Offcanvas.Header>
            <Navbar.Brand as={Link} to="/frontpage" className="p-0" onClick={handleClose}>
              <SmallLogo/>
            </Navbar.Brand>
            <button type="button" className="btn-none ms-auto" onClick={handleClose} aria-label="Close">
              <Icon name="close" size={24}/>
            </button>
          </Offcanvas.Header>

          <Offcanvas.Body className="align-items-lg-center d-flex flex-column flex-lg-row w-100">
            <Nav className="navbar-nav w-100 w-lg-auto me-lg-auto mb-5 mb-lg-0 gap-lg-4">
              <Nav.Item>
                <Nav.Link as={NavLink} to="/dash" className={navLinkClass} onClick={handleClose}>
                  Dashboards
                </Nav.Link>
              </Nav.Item>

              <Nav.Item>
                <Nav.Link as={NavLink} to="/product" className={navLinkClass} onClick={handleClose}>
                  Product
                </Nav.Link>
              </Nav.Item>

              <Nav.Item>
                <Nav.Link as={NavLink} to="/docs/getting-started" className={navLinkClass} onClick={handleClose}>
                  Docs
                </Nav.Link>
              </Nav.Item>

              <Nav.Item>
                <Nav.Link as={NavLink} to="/about" className={navLinkClass} onClick={handleClose}>
                  About
                </Nav.Link>
              </Nav.Item>

              <Nav.Item>
                <Nav.Link href="https://blog.nyrkio.com/" onClick={handleClose}>
                  Blog
                </Nav.Link>
              </Nav.Item>
            </Nav>

            {loggedIn ? (
              <UserMenu loggedIn={loggedIn} setLoggedIn={setLoggedIn}/>
            ) : (
              <div className="loginmenu d-flex gap-3 gap-xl-4 mt-auto mt-lg-0">
                <Link
                  to="/signup"
                  className="btn btn-outline-primary signupbutton w-100 w-lg-auto"
                  onClick={handleClose}
                >
                  Create account
                </Link>
                <Link
                  to="/login"
                  className="btn btn-primary loginbutton w-100 w-lg-auto"
                  onClick={handleClose}
                >
                  Log in
                </Link>
              </div>
            )}

            <div className="nyrkio-login-controls">
              <ImpersonateControls/>
            </div>

          </Offcanvas.Body>
        </Navbar.Offcanvas>
      </Container>
    </Navbar>
  );
};
