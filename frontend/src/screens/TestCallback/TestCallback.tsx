import { useEffect, useState } from "react";

export const TestCallback = () => {
  const [params, setParams] = useState<Record<string, string>>({});
  const [currentUrl, setCurrentUrl] = useState("");

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const paramsObj: Record<string, string> = {};
    
    urlParams.forEach((value, key) => {
      paramsObj[key] = value;
    });
    
    setParams(paramsObj);
    setCurrentUrl(window.location.href);
  }, []);

  return (
    <div style={{ padding: "2rem", fontFamily: "monospace" }}>
      <h1>OAuth Callback Test Page</h1>
      
      <div style={{ marginBottom: "1rem" }}>
        <h3>Current URL:</h3>
        <p style={{ wordBreak: "break-all", background: "#f5f5f5", padding: "10px" }}>
          {currentUrl}
        </p>
      </div>
      
      <div style={{ marginBottom: "1rem" }}>
        <h3>URL Parameters:</h3>
        <pre style={{ background: "#f5f5f5", padding: "10px" }}>
          {JSON.stringify(params, null, 2)}
        </pre>
      </div>
      
      <div style={{ marginBottom: "1rem" }}>
        <h3>Local Storage:</h3>
        <pre style={{ background: "#f5f5f5", padding: "10px" }}>
          access_token: {localStorage.getItem("access_token") ?? "not found"}
        </pre>
      </div>
      
      <div>
        <h3>Actions:</h3>
        <button 
          onClick={() => window.location.href = "/calendar"}
          style={{ margin: "5px", padding: "10px 15px" }}
        >
          Go to Calendar
        </button>
        <button 
          onClick={() => window.location.href = "/reg-page"}
          style={{ margin: "5px", padding: "10px 15px" }}
        >
          Go to Registration
        </button>
        <button 
          onClick={() => localStorage.clear()}
          style={{ margin: "5px", padding: "10px 15px" }}
        >
          Clear Storage
        </button>
      </div>
    </div>
  );
};

export default TestCallback;
