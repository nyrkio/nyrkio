import { Link } from "react-router-dom";
import { BackButton } from "./BackButton";
export function NoMatch() {
  return (
    <div className="container text-center justify-content-center p-5">
      <h2>
        <div className="text-primary">404</div>
        <div className="h3 text-secondary">OOPS...</div>
      </h2>
      <p className="my-4">This page not found!</p>
      <BackButton className="btn btn-primary" />
    </div>
  );
}
