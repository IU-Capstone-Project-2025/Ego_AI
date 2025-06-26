import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './Auth.css';

export const Auth: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  
  // Получаем страницу, с которой пользователь был перенаправлен
  const from = location.state?.from?.pathname || '/chat';
  const authError = location.state?.error;

  const handleGoogleAuth = async () => {
    setIsLoading(true);
    
    try {
      // Проверяем нужно ли использовать бэкенд
      const useBackend = import.meta.env.VITE_BACKEND_USE !== 'false';
      
      if (useBackend) {
        // Реальная интеграция с Google OAuth
        // Передаем информацию о том, куда перенаправить после авторизации
        const redirectTo = encodeURIComponent(from);
        window.location.href = `/api/v1/auth/google?redirect_to=${redirectTo}`;
        return;
      }
      
      // Если бэкенд не используется, имитируем процесс аутентификации
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // После успешной аутентификации перенаправляем на исходную страницу
      navigate(from, { replace: true });
    } catch (error) {
      console.error('Authentication failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-background">
        <div className="auth-card">
          <div className="auth-header">
            <div className="auth-logo">
              <span className="logo-text">EGO:<span className="logo-highlight">AI</span></span>
            </div>
            <h1 className="auth-title">Welcome Back</h1>
            <p className="auth-subtitle">Sign in to continue to your AI assistant</p>
          </div>

          {authError && (
            <div style={{
              padding: '1rem',
              margin: '1rem 0',
              backgroundColor: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              borderRadius: '8px',
              color: '#dc2626',
              fontSize: '0.875rem',
              textAlign: 'center'
            }}>
              Authentication failed: {authError}
            </div>
          )}

          <div className="auth-content">
            <button 
              onClick={handleGoogleAuth}
              disabled={isLoading}
              className="google-auth-btn"
            >
              {isLoading ? (
                <div className="loading-spinner" />
              ) : (
                <>
                  <svg className="google-icon" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                  </svg>
                  Continue with Google
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}; 