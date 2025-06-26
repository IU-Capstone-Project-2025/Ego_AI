// API utility functions for making authenticated requests
const API_BASE_URL = (import.meta as any).env.VITE_API_URL ?? "http://egoai-api.duckdns.org";

export const getAuthToken = (): string | null => {
  return localStorage.getItem("access_token");
};

export const isAuthenticated = (): boolean => {
  const token = getAuthToken();
  return !!token;
};

export const logout = async (): Promise<void> => {
  try {
    // Call the logout endpoint to clear the HTTP-only cookie
    await fetch(`${API_BASE_URL}/api/v1/auth/logout`, {
      method: 'POST',
      credentials: 'include',
    });
  } catch (error) {
    console.error('Logout request failed:', error);
  }
  // Remove token from localStorage
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
    credentials: 'include', // Include HTTP-only cookies as fallback
  };
  
  try {
    const response = await fetch(url, config);
    
    // Handle unauthorized responses
    if (response.status === 401) {
      await logout();
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
