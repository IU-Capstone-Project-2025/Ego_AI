import React, { useEffect } from "react";
import "./RegPage.css";
import gLogo from "./res/gLogo.png";

const handleGoogleLogin = () => {
  window.location.href = "http://localhost:8000/api/v1/auth/google-login"
};

export const RegPage = () => {
  // Handle Google OAuth callback
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get("token");
    if (token) {
      // Store token (localStorage or cookie)
      localStorage.setItem("access_token", token);
      // Redirect to main app page (change path as needed)
      window.location.href = "/calendar";
    }
  }, []);

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
            />
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
            />
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