import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

export const AuthCallback: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    // Получаем параметры из URL (success, error, redirect_to, token)
    const success = searchParams.get('success');
    const error = searchParams.get('error');
    const token = searchParams.get('token');
    const redirectTo = searchParams.get('redirect_to') || '/chat';

    if (token) {
      // Сохраняем токен в localStorage
      localStorage.setItem('access_token', token);
      // Успешная авторизация - перенаправляем на исходную страницу
      navigate(redirectTo, { replace: true });
    } else if (success === 'true') {
      // Успешная авторизация без токена в URL (использует cookie)
      navigate(redirectTo, { replace: true });
    } else if (error) {
      // Ошибка авторизации - показываем ошибку и перенаправляем на страницу входа
      console.error('Auth error:', error);
      navigate('/auth', { 
        replace: true,
        state: { error: decodeURIComponent(error) }
      });
    } else {
      // Неизвестный статус - перенаправляем на страницу входа
      navigate('/auth', { replace: true });
    }
  }, [navigate, searchParams]);

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
        }}>Completing authentication...</p>
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
}; 