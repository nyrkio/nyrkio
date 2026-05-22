import { useState } from "react";
import Icon from "./../Icon.jsx";
import './PasswordInput.scss';

export const PasswordInput = ({ id, placeholder, className = "form-control", onChange, value }) => {
  const [showPassword, setShowPassword] = useState(false);

  const togglePasswordVisibility = () => {
    setShowPassword((prev) => !prev);
  };

  return (
    <div className="password-toggle-wrapper">
      <input
        type={showPassword ? "text" : "password"}
        id={id}
        placeholder={placeholder}
        className={`pe-6 ${className}`}
        onChange={onChange}
        value={value}
      />
      <button
        className="btn-none"
        type="button"
        onClick={togglePasswordVisibility}
        style={{ zIndex: 4 }}
        aria-label={showPassword ? "Hide password" : "Show password"}
      >
        <Icon name={showPassword ? "eye-crossed" : "eye"} size={24} />
      </button>
    </div>
  );
};
