// API utility functions for making authenticated requests
const API_BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export const getAuthToken = (): string | null => {
  return localStorage.getItem("access_token");
};

export const isAuthenticated = (): boolean => {
  const token = getAuthToken();
  return !!token;
};

export const logout = (): void => {
  localStorage.removeItem("access_token");
  // Instead of direct redirect, we'll let the calling component handle navigation
  // This allows for better React Router integration
};

export const apiRequest = async (
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> => {
  const token = getAuthToken();
  const url = `${API_BASE_URL}/api/v1${endpoint}`;
  
  const defaultHeaders: Record<string, string> = {
    "Content-Type": "application/json",
  };
  
  if (token) {
    defaultHeaders.Authorization = `Bearer ${token}`;
  }
  
  const config: RequestInit = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };
  
  try {
    const response = await fetch(url, config);
    
    // Handle unauthorized responses
    if (response.status === 401) {
      logout();
      throw new Error("Authentication required");
    }
    
    return response;
  } catch (error) {
    console.error("API request failed:", error);
    throw error;
  }
};

// Helper functions for common HTTP methods
export const apiGet = (endpoint: string): Promise<Response> =>
  apiRequest(endpoint, { method: "GET" });

export const apiPost = (endpoint: string, data?: any): Promise<Response> =>
  apiRequest(endpoint, {
    method: "POST",
    body: data ? JSON.stringify(data) : undefined,
  });

export const apiPut = (endpoint: string, data?: any): Promise<Response> =>
  apiRequest(endpoint, {
    method: "PUT",
    body: data ? JSON.stringify(data) : undefined,
  });

export const apiDelete = (endpoint: string): Promise<Response> =>
  apiRequest(endpoint, { method: "DELETE" });
