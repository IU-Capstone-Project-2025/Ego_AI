import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export const LoginCallback = () => {
  const navigate = useNavigate();
  
  useEffect(() => {
    console.log("LoginCallback: Component mounted");
    console.log("LoginCallback: Current URL:", window.location.href);
    
    const params = new URLSearchParams(window.location.search);
    const token = params.get("token");
    
    console.log("LoginCallback: URL params:", params.toString());
    console.log("LoginCallback: Token found:", !!token);
    
    if (token) {
      console.log("LoginCallback: Token received:", token.substring(0, 20) + "...");
      // Store the JWT token
      // Additional logging for debugging
      console.log("LoginCallback: Redirecting to calendar with token:", token);
      console.log("LoginCallback: localStorage before storing token:", localStorage);

      // Error handling for localStorage
      try {
        // Validate token before storing
        if (!token || token.trim() === "") {
          console.error("LoginCallback: Invalid token received, cannot store in localStorage");
          navigate("/reg-page", { replace: true });
          return;
        }

        // Debugging localStorage availability
        localStorage.setItem("test", "test");
        localStorage.removeItem("test");
        console.log("LoginCallback: localStorage is available");

        localStorage.setItem("access_token", token);
        console.log("LoginCallback: Token successfully stored in localStorage");

        // Log the token value for debugging
        console.log("LoginCallback: Token value before storing:", token);

        // Log the localStorage state after storing
        setTimeout(() => {
          console.log("LoginCallback: localStorage state after storing token:", localStorage);
        }, 100);
      } catch (error) {
        console.error("LoginCallback: Error storing token in localStorage:", error);
        navigate("/reg-page", { replace: true });
        return;
      }
      console.log("LoginCallback: Token stored, redirecting to calendar");
      
      // Ensure token is stored before redirecting
      setTimeout(() => {
        const storedToken = localStorage.getItem("access_token");
        if (storedToken) {
          console.log("LoginCallback: Token verified in localStorage, navigating to calendar");
          navigate("/calendar", { replace: true });
        } else {
          console.error("LoginCallback: Token not found in localStorage, staying on callback page");
        }
      }, 500);
    } else {
      // Handle error case - redirect back to registration
      console.error("LoginCallback: No token received from OAuth callback");
      setTimeout(() => {
        navigate("/reg-page", { replace: true });
      }, 500);
    }
  }, [navigate]);

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      height: '100vh',
      fontSize: '18px'
    }}>
      <div>
        <h2>Authenticating...</h2>
        <p>Please wait while we log you in.</p>
      </div>
    </div>
  );
};

export default LoginCallback;
