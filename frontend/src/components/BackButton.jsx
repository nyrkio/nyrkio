import { useNavigate } from "react-router-dom";

export const BackButton = ({ className }) => {
  const navigate = useNavigate();

  const handleBack = () => {
    // Check if there is internal history to go back to
    if (window.history.length > 2) {
      navigate(-1);
    } else {
      navigate("/", { replace: true }); // Fallback to home
    }
  };

  return <button onClick={handleBack} className={className}>Back</button>;
}
