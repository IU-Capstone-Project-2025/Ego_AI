import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./RegPage.css";
import gLogo from "./res/gLogo.png";

const handleGoogleLogin = () => {
  // Use environment variable for API URL, fallback to localhost for development
  const apiUrl = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
  window.location.href = `${apiUrl}/api/v1/auth/google-login`;
};

export const RegPage = () => {
  const navigate = useNavigate();
  
  // Check if user is already authenticated
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      // User is already logged in, redirect to calendar
      navigate("/calendar", { replace: true });
    }
  }, [navigate]);

  return (
    <div className="regpage-container">
      <div className="regpage-content">
        <h1 className="regpage-title">REGISTER OR LOGIN TO USE</h1>
        <h2 className="regpage-logo">
          <span className="ego">EGO</span>
          <span className="colon">:</span>
          <span className="ai">AI</span>
        </h2>
        <div className="regpage-buttons">
          <button 
            className="google-btn"
            onClick={handleGoogleLogin}
          >
            <img
              src={gLogo}
              alt="Sign In"
              className="google-icon"
              style={{ width: 32, height: 32, marginRight: 12 }}
            />{" "}
            Sign In with Google
          </button>
          <button 
            className="google-btn"
            onClick={handleGoogleLogin}
          >
            <img
              src={gLogo}
              alt="Sign Up"
              className="google-icon"
              style={{ width: 32, height: 32, marginRight: 12 }}
            />{" "}
            Sign Up with Google
          </button>
        </div>
      </div>
      <div className="regpage-footer">
        <span className="ego">EGO</span>
        <span className="colon">:</span>
        <span className="ai">AI</span>
      </div>
    </div>
  );
};

export default RegPage;