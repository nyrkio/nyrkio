import ToS from "../static/doc/Nyrkio Terms of Service v2 - 2026-02-19.pdf";
import PrivacyPolicy from "../static/doc/Privacy Policy Nyrkiö 2024 v1.0.pdf";
import { Link } from "react-router-dom";

export const LegalPage = () => {
  return (
    <>
      <div className="container legal-page text-center">
        <h1 className="mb-5 text-primary ">Legal documents</h1>
        <div className="d-flex gap-6 justify-content-center">
          <Link rel="noopener noreferrer" to={ToS} target="_blank">
            Terms of Service
          </Link>
          <Link rel="noopener noreferrer" to={PrivacyPolicy} target="_blank">
            Privacy Policy
          </Link>
        </div>
      </div>
    </>
  );
};
