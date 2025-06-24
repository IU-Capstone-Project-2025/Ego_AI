import React, { useState, useRef, useEffect } from 'react';
import '../../components/Layout.css';
import './Chat.css';

interface Message {
  sender: 'user' | 'llm';
  text: string;
}

export const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMessage: Message = { sender: 'user', text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');

    // Имитация ответа LLM (заменить на реальный запрос к API)
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        { sender: 'llm', text: 'Это ответ LLM на: ' + userMessage.text },
      ]);
    }, 1000);
  };

  const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-container">
      {messages.length === 0 ? (
        <div className="chat-welcome">
          <div className="welcome-text">
            <h1 className="greeting">HI USERNAME</h1>
            <h2 className="question">WHAT WOULD LIKE TO DISCUSS TODAY?</h2>
          </div>
        </div>
      ) : (
        <div className="chat-messages">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`chat-message ${msg.sender === 'user' ? 'user' : 'llm'}`}
            >
              <div className="chat-message-content">
                {msg.text}
              </div>
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>
      )}
      
      <div className="chat-input-section">
        <div className="chat-input-container">
          <div className="input-branding">
            <span className="input-brand-text">EGO:<span className="input-brand-highlight">AI</span></span>
          </div>
          <div className="chat-input-wrapper">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleInputKeyDown}
              placeholder="Message EGO:AI..."
              className="chat-input"
            />
            <div className="chat-button-group">
              <button className="chat-mic-btn">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <path d="M12 15C13.66 15 15 13.66 15 12V6C15 4.34 13.66 3 12 3C10.34 3 9 4.34 9 6V12C9 13.66 10.34 15 12 15Z" fill="currentColor"/>
                  <path d="M19 12C19 15.53 16.39 18.44 13 18.93V21H11V18.93C7.61 18.44 5 15.53 5 12H7C7 14.76 9.24 17 12 17C14.76 17 17 14.76 17 12H19Z" fill="currentColor"/>
                </svg>
              </button>
              <button 
                onClick={sendMessage} 
                className="chat-send-btn"
                disabled={!input.trim()}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <path d="M2.01 21L23 12L2.01 3L2 10L17 12L2 14L2.01 21Z" fill="currentColor"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
