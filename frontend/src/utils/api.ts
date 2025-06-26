// API utility functions for making authenticated requests
const API_BASE_URL = (import.meta as any).env.VITE_API_URL ?? "http://egoai.duckdns.org:8000";

export const getAuthToken = (): string | null => {
  // Tokens are stored in HTTP-only cookies managed by the backend
  return null;
};

export const isAuthenticated = (): boolean => {
  // Authentication status should be checked via API call to /users/me
  return false;
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
};

export const apiRequest = async (
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> => {
  const url = `${API_BASE_URL}/api/v1${endpoint}`;
  
  const defaultHeaders: Record<string, string> = {
    "Content-Type": "application/json",
  };
  
  const config: RequestInit = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
    credentials: 'include', // Always include cookies
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
