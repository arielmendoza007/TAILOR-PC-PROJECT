// src/components/Chat.jsx
import React, { useState } from 'react';
import { sendMessageToMariana } from '../api';
import BudgetWidget from './BudgetWidget';

export default function Chat() {
  const [messages, setMessages] = useState([{ sender: 'Mariana', text: 'Hola, ¿qué traes?' }]);
  const [input, setInput] = useState('');
  const [showBudget, setShowBudget] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    const newMessages = [...messages, { sender: 'User', text: input }];
    setMessages(newMessages);
    setInput('');
    setLoading(true);

    // Llamada a la API
    const response = await sendMessageToMariana(input);
    
    setMessages([...newMessages, { sender: 'Mariana', text: response.text }]);
    setLoading(false);

    // El Interceptor: Si el JSON trae el comando, abrimos el widget
    if (response.system_command === "OPEN_BUDGET") {
      setShowBudget(true);
    }
  };

  return (
    <div className="chat-container">
      <div className={`chat-window ${showBudget ? 'dimmed' : ''}`}>
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.sender === 'Mariana' ? 'bot' : 'user'}`}>
            <strong>{msg.sender}:</strong> {msg.text}
          </div>
        ))}
        {loading && <div className="message bot">Escribiendo...</div>}
      </div>

      {/* Renderizado condicional del Easter Egg */}
      {showBudget && <BudgetWidget onClose={() => setShowBudget(false)} />}

      <div className="input-area">
        <input 
          type="text" 
          value={input} 
          onChange={(e) => setInput(e.target.value)} 
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Escríbele a Mariana..."
        />
        <button onClick={handleSend}>Enviar</button>
      </div>
    </div>
  );
}