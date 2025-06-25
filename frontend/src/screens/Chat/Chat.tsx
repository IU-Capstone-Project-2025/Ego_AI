import React, { useState, useRef, useEffect } from 'react';
import '../../components/Layout.css';
import './Chat.css';
import { chatWithML } from '@/utils/mlApi';
import { createEvent } from '@/utils/calendarApi';

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

    try {
      const result = await chatWithML(userMessage.text);
      let llmText = result.response ?? "No responce for LLM service.";
      // Try to parse as JSON for event creation
      try {
        const eventCandidate = JSON.parse(llmText);
        if (eventCandidate && eventCandidate.title && eventCandidate.start_time && eventCandidate.end_time) {
          // Patch type if missing or invalid
          const validTypes = ['focus', 'tasks', 'target', 'other'];
          if (!validTypes.includes(eventCandidate.type)) {
            eventCandidate.type = 'other';
          }
          await createEvent(eventCandidate);
          llmText = 'Задача успешно добавлена в календарь!';
        }
      } catch (e) { /* not a JSON, just a normal reply */ }
      setMessages((prev) => [
        ...prev,
        { sender: 'llm', text: llmText }
      ]);
    } catch (error) {
      console.error('Error connecting to ML service:', error);
      setMessages((prev) => [
        ...prev,
        { sender: 'llm', text: 'Error not connect to ML service'}
      ]);
    }
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
