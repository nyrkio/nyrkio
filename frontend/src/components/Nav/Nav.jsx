import { Link, NavLink } from "react-router-dom";
import { useState, useEffect } from "react";
import { Navbar, Container, Offcanvas, Nav, NavDropdown } from "react-bootstrap";
import { UserMenu } from "./../UserMenu.jsx";
import { SmallLogo } from "./../Logo";
import { ImpersonateControls } from "./../ImpersonateControls";
import "./Nav.scss";
import { Icon } from "../Icon.jsx";

const navLinkClass = ({ isActive }) =>
  `nav-link ${isActive ? "active" : ""}`;

export const NavHeader = ({ loggedIn, setLoggedIn }) => {
  const [showMenu, setShowMenu] = useState(false);

  const handleClose = () => setShowMenu(false);
  const handleShow = () => setShowMenu(true);

  // Close offcanvas when window is resized to lg+ breakpoint
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 1024) {
        setShowMenu(false);
      }
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return (
    <Navbar
      expand="lg"
      className="navbar-site align-items-center navbar-light bg-white navbar-top shadow px-3 py-3 my-4 mb-lg-7 rounded-2 gap-2 gap-xl-4"
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
            <Nav className="navbar-nav w-100 w-lg-auto me-lg-auto mb-5 mb-lg-0 gap-lg-2 gap-xxl-4">

              {/* Dashboards dropdown */}
              <NavDropdown title="Dashboards" id="dashboards-dropdown" renderMenuOnMount>
                {loggedIn ? (
                  <>
                    <NavDropdown.Item as={NavLink} to="/tests" onClick={handleClose}>
                      My Dashboard
                    </NavDropdown.Item>
                    <NavDropdown.Item as={NavLink} to="/orgs" onClick={handleClose}>
                      Org Dashboards
                    </NavDropdown.Item>
                    <NavDropdown.Item as={NavLink} to="/public" onClick={handleClose}>
                      Public Dashboards
                    </NavDropdown.Item>
                    <NavDropdown.Item as={NavLink} to="/frontpage" onClick={handleClose}>
                      Front page
                    </NavDropdown.Item>
                  </>
                ) : (
                  <>
                    <NavDropdown.Item as={NavLink} to="/docs/getting-started" onClick={handleClose}>
                      Create My Dashboard
                    </NavDropdown.Item>
                    <NavDropdown.Item as={NavLink} to="/public" onClick={handleClose}>
                      Public Dashboards
                    </NavDropdown.Item>
                    <NavDropdown.Item as={NavLink} to="/frontpage" onClick={handleClose}>
                      Front page
                    </NavDropdown.Item>
                  </>
                )}
              </NavDropdown>

              {/* Product dropdown */}
              <NavDropdown title="Product" id="product-dropdown" renderMenuOnMount>
                <NavDropdown.Item as={NavLink} to="/product" end onClick={handleClose}>
                  Nyrkiö Change Detection
                </NavDropdown.Item>
                <NavDropdown.Item as={NavLink} to="/product/user-testimonials" onClick={handleClose}>
                  What our users say
                </NavDropdown.Item>
                {loggedIn && (
                  <NavDropdown.Item as={NavLink} to="/billing" onClick={handleClose}>
                    Billing
                  </NavDropdown.Item>
                )}
              </NavDropdown>

              {/* Docs dropdown */}
              <NavDropdown title="Docs" id="docs-dropdown" renderMenuOnMount>
                <NavDropdown.Item as={NavLink} to="/docs/getting-started" onClick={handleClose}>
                  Nyrkio Runners
                </NavDropdown.Item>
                <NavDropdown.Item as={NavLink} to="/docs/change-detection" onClick={handleClose}>
                  Change Detection
                </NavDropdown.Item>
                <NavDropdown.Item as={NavLink} to="/docs/getting-started-http" onClick={handleClose}>
                  HTTP API
                </NavDropdown.Item>
                <NavDropdown.Item as={NavLink} to="/docs/working-with-graphs" onClick={handleClose}>
                  Working with the graphs
                </NavDropdown.Item>
                <NavDropdown.Item as={NavLink} to="/docs/git-perf-plugin" onClick={handleClose}>
                  git-perf plugin
                </NavDropdown.Item>
                <NavDropdown.Item as={NavLink} to="/docs/teams" onClick={handleClose}>
                  Teams / Orgs
                </NavDropdown.Item>
                <NavDropdown.Item href="/openapi" onClick={handleClose}>
                  API
                </NavDropdown.Item>
              </NavDropdown>

              {/* About dropdown */}
              <NavDropdown title="About" id="about-dropdown" renderMenuOnMount>
                <NavDropdown.Item as={NavLink} to="/about" end onClick={handleClose}>
                  About Nyrkiö Oy
                </NavDropdown.Item>
                <NavDropdown.Item as={NavLink} to="/about/ecosystem" onClick={handleClose}>
                  Open Source Ecosystem
                </NavDropdown.Item>
                <NavDropdown.Item as={NavLink} to="/legal" onClick={handleClose}>
                  Legal
                </NavDropdown.Item>
                <NavDropdown.Item as={NavLink} to="/legend" onClick={handleClose}>
                  The Legend of Nyyrikki
                </NavDropdown.Item>
              </NavDropdown>

              <Nav.Item>
                <Nav.Link href="https://blog.nyrkio.com/" target="_blank" onClick={handleClose}>
                  Blog
                </Nav.Link>
              </Nav.Item>

              <Nav.Item>
                <Nav.Link as={NavLink} to="/pricing" className={navLinkClass} onClick={handleClose}>
                  Pricing
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
