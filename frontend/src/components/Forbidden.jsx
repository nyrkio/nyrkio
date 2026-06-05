import { BackButton } from "./BackButton";
import {Link} from "react-router-dom";
export const Forbidden = () => {
  return (
    <div className="container text-center justify-content-center p-5">
      <h2>
        <div className="text-primary">403</div>
        <div className="h3 text-secondary">OOPS...</div>
      </h2>

      <p className="my-4">
        You don't have permission to view this page.
      </p>

      <div className="d-flex flex-column flex-md-row justify-content-center gap-3">
        <Link className="btn btn-primary w-100 w-md-auto" to='/login'>Log in</Link>
        <BackButton className="btn btn-outline-primary w-100 w-md-auto" />
      </div>
    </div>
  );
};
