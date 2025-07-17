import React, { useEffect, useMemo, useRef, useState } from "react";
import "./CIEChatBot.css";

const MyChatBot = () => {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const ws = useRef(null);

  const sessionId = useMemo(() => {
    const storedId = localStorage.getItem("studyAssistantSessionId");
    return storedId || crypto.randomUUID();
  }, []);

  useEffect(() => {
    localStorage.setItem("studyAssistantSessionId", sessionId);
    console.log(sessionId)
    ws.current = new WebSocket(`ws://localhost:8000/ws/${sessionId}`);
    console.log("Websocket Initialized, Trying to connect")
    ws.current.onopen = () => setIsConnected(true);

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === data.correlation_id
            ? {
                ...msg,
                content: data.response,
                isLoading: false,
                timestamp: new Date(),
              }
            : msg
        )
      );
    };

    ws.current.onclose = () => {
      setIsConnected(false);
      setTimeout(() => {
        if (!ws.current || ws.current.readyState === WebSocket.CLOSED) {
          ws.current = new WebSocket(
            `wss://api.your-university.edu/ws/${sessionId}`
          );
        }
      }, 3000);
    };

    return () => {
      if (ws.current) ws.current.close();
    };
  }, [sessionId]);

  const handleSubmit = () => {
    if (!input.trim() || !isConnected) return;

    const correlationId = crypto.randomUUID();

    const userMessage = {
      id: correlationId,
      content: input,
      isUser: true,
      timestamp: new Date(),
    };

    const assistantPlaceholder = {
      id: `${correlationId}-assistant`,
      content: "Thinking...",
      isLoading: true,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage, assistantPlaceholder]);

    if (ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(
        JSON.stringify({
          session_id: sessionId,
          correlation_id: correlationId,
          question: input,
        })
      );
    }

    setInput("");
  };

  const formatTime = (date) =>
    date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

  return (
    <div className="chat-container">
      <div className="header">
        College Study Assistant
        <span
          style={{
            fontSize: "0.8rem",
            marginLeft: "10px",
            color: isConnected ? "#a7f3d0" : "#fca5a5",
          }}
        >
          {isConnected ? "Connected" : "Connecting..."}
        </span>
      </div>

      <div className="messages">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`message ${
              message.isUser ? "user-message" : "assistant-message"
            }`}
          >
            {message.content}
            {message.isLoading && (
              <span className="typing-indicator">
                <span className="typing-dot"></span>
                <span className="typing-dot"></span>
                <span className="typing-dot"></span>
              </span>
            )}
            <div className="timestamp">{formatTime(message.timestamp)}</div>
          </div>
        ))}
      </div>

      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
          placeholder="Ask about your course materials..."
          disabled={!isConnected}
        />
        <button onClick={handleSubmit} disabled={!input.trim() || !isConnected}>
          Send
        </button>
      </div>
    </div>
  );
};

export default MyChatBot;
