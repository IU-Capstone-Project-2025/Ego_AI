import React, { useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

interface User {
  id: string;
  email: string;
  name: string;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const location = useLocation();

  useEffect(() => {
    // Проверяем переменную окружения для защиты маршрутов
    const isProtectionEnabled = (import.meta as any).env.VITE_PROTECTED !== 'false';
    
    if (!isProtectionEnabled) {
      // Если защита отключена, сразу разрешаем доступ
      setIsAuthenticated(true);
      setUser({
        id: 'dev-user',
        email: 'dev@example.com',
        name: 'Development User'
      });
      return;
    }

    // Проверяем нужно ли использовать бэкенд
    const useBackend = (import.meta as any).env.VITE_BACKEND_USE !== 'false';
    
    if (!useBackend) {
      // Если бэкенд не используется, имитируем успешную авторизацию
      setTimeout(() => {
        setIsAuthenticated(true);
        setUser({
          id: 'dummy-user',
          email: 'dummy@example.com',
          name: 'Dummy User'
        });
      }, 500); // Небольшая задержка для имитации запроса
      return;
    }

    // Если защита включена и бэкенд используется, проверяем авторизацию
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const API_BASE_URL = (import.meta as any).env.VITE_API_URL ?? "http://egoai.duckdns.org:8000";
      const response = await fetch(`${API_BASE_URL}/api/v1/users/me`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Включаем cookies для сессии
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        setIsAuthenticated(true);
      } else if (response.status === 401) {
        // Пользователь не авторизован
        setIsAuthenticated(false);
        setUser(null);
      } else {
        // Другие ошибки (сервер недоступен и т.д.)
        console.error('Auth check failed:', response.status);
        setIsAuthenticated(false);
      }
    } catch (error) {
      console.error('Auth check error:', error);
      setIsAuthenticated(false);
    }
  };

  // Показываем загрузку пока проверяем авторизацию
  if (isAuthenticated === null) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #f8fffe 0%, #f3f8f6 25%, #f7f5ff 50%, #f0fdf4 75%, #faf5ff 100%)'
      }}>
        <div style={{
          textAlign: 'center',
          padding: '2rem',
          background: 'rgba(255, 255, 255, 0.9)',
          backdropFilter: 'blur(20px)',
          borderRadius: '16px',
          boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)',
          border: '1px solid rgba(255, 255, 255, 0.3)'
        }}>
          <div style={{
            width: '40px',
            height: '40px',
            border: '3px solid #e5e7eb',
            borderTop: '3px solid #10a37f',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 1rem auto'
          }}></div>
          <p style={{
            margin: 0,
            fontSize: '1rem',
            color: '#6b7280',
            fontWeight: 500
          }}>Checking authentication...</p>
        </div>
        <style dangerouslySetInnerHTML={{
          __html: `
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          `
        }} />
      </div>
    );
  }

  // Если пользователь не авторизован, перенаправляем на страницу аутентификации
  if (!isAuthenticated) {
    return <Navigate to="/auth" state={{ from: location }} replace />;
  }

  // Если пользователь авторизован, показываем защищенный контент
  return <>{children}</>;
}; 