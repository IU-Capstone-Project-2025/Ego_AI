import React, { useState, useEffect } from 'react';
import './HomePage.css';

interface ApiResponse {
  message: string;
}

const HomePage: React.FC = () => {
  const [message, setMessage] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');

  const fetchHelloWorld = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await fetch('/hello-world');
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data: ApiResponse = await response.json();
      setMessage(data.message);
    } catch (err) {
      setError('Ошибка при получении данных с сервера');
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHelloWorld();
  }, []);

  return (
    <div className="home-page">
      <header className="page-header">
        <h1>Ego AI Frontend</h1>
        <div className="message-container">
          {loading && <p>Загрузка...</p>}
          {error && <p className="error">{error}</p>}
          {message && !loading && !error && (
            <div>
              <h2>Сообщение с сервера:</h2>
              <p className="message">{message}</p>
            </div>
          )}
        </div>
        <button 
          onClick={fetchHelloWorld} 
          disabled={loading}
          className="refresh-button"
        >
          {loading ? 'Загрузка...' : 'Обновить'}
        </button>
      </header>
    </div>
  );
};

export default HomePage; 