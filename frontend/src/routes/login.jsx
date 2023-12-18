import { Form } from "react-router-dom";

export default function Login() {
  return (
    <div className="row">
      <Form>
        <div className="mb-3">
          <label htmlFor="exampleInputEmail1" className="form-label">
            Email address
          </label>
          <input
            type="email"
            className="form-control"
            id="exampleInputEmail1"
          />
          <div className="mb-3 p-5">
            <label htmlFor="exampleInputPassword1" className="form-label">
              Password
            </label>
            <input
              type="password"
              className="form-control"
              id="exampleInputPassword1"
            />
          </div>
        </div>
        <button type="submit" className="btn btn-success">
          Submit
        </button>
      </Form>
    </div>
  );
}
