import ToS from "../static/doc/Terms Of Service 1.0.pdf";
import PrivacyPolicy from "../static/doc/Privacy Policy Nyrkiö 2024 v1.0.pdf";
import { Link } from "react-router-dom";

export const LegalPage = () => {
  return (
    <>
      <div className="container legal-page">
        <div className="row col-xl-10 mt-8 p-5">
          <h1 className="mb-5">Legal documents</h1>
          <p>
            <Link to={ToS} target="_blank">
              Terms of Service
            </Link>
          </p>
          <p>
            <Link to={PrivacyPolicy} target="_blank">
              Privacy Policy
            </Link>
          </p>
        </div>
      </div>
    </>
  );
};
