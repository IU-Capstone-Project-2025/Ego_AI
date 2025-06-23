import { useState, useEffect } from "react";
import { getAuthToken, isAuthenticated, logout } from "../utils/api";

interface UseAuthReturn {
  isAuth: boolean;
  token: string | null;
  loading: boolean;
  signOut: () => void;
}

export const useAuth = (): UseAuthReturn => {
  const [isAuth, setIsAuth] = useState<boolean>(false);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const checkAuth = () => {
      const authToken = getAuthToken();
      const authenticated = isAuthenticated();
      
      setToken(authToken);
      setIsAuth(authenticated);
      setLoading(false);
    };

    checkAuth();
    
    // Listen for storage changes (in case of logout in another tab)
    const handleStorageChange = () => {
      checkAuth();
    };
    
    window.addEventListener('storage', handleStorageChange);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  const signOut = () => {
    logout();
  };

  return {
    isAuth,
    token,
    loading,
    signOut,
  };
};
