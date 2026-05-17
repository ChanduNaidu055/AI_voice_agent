import { useState, useEffect, useRef } from "react";
import { Mic, Square, Activity, User, Bot } from "lucide-react";
import "./index.css";

export default function Home() {
  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text: "Hello Chandu! I am your AI Assistant. How can I help you today?",
    },
  ]);
  const [isRecording, setIsRecording] = useState(false);
  const [isConnected, setIsConnected] = useState(false);

  const ws = useRef(null);
  const mediaRecorder = useRef(null);
  const audioChunks = useRef([]);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    const backendUrl = import.meta.env.VITE_BACKEND_URL || "ws://localhost:8000";
    ws.current = new WebSocket(`${backendUrl}/ws/chat`);

    ws.current.onopen = () => setIsConnected(true);
    ws.current.onclose = () => setIsConnected(false);

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.text) {
        setMessages((prev) => [...prev, { sender: "bot", text: data.text }]);
      }
      if (data.audio) {
        const audio = new Audio("data:audio/mp3;base64," + data.audio);
        audio.play();
      }
    };

    return () => ws.current?.close();
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream);

      mediaRecorder.current.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunks.current.push(e.data);
      };

      mediaRecorder.current.onstop = () => {
        const audioBlob = new Blob(audioChunks.current, { type: "audio/webm" });
        if (ws.current.readyState === WebSocket.OPEN) {
          ws.current.send(audioBlob);
          setMessages((prev) => [
            ...prev,
            { sender: "user", text: "🎤 Audio Message Sent..." },
          ]);
        }
        audioChunks.current = [];
      };

      mediaRecorder.current.start();
      setIsRecording(true);
    } catch (err) {
      alert("Microphone access denied!");
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current && isRecording) {
      mediaRecorder.current.stop();
      mediaRecorder.current.stream.getTracks().forEach((track) => track.stop());
      setIsRecording(false);
    }
  };

  return (
    <div className="app-container">
      <header className="header">
        <Activity className="logo-icon" />
        <h1>2Care.ai Clinic</h1>
        <span className={`status ${isConnected ? "online" : "offline"}`}>
          {isConnected ? "Connected" : "Disconnected"}
        </span>
      </header>

      <div className="chat-window">
        {messages.map((msg, index) => (
          <div key={index} className={`message-wrapper ${msg.sender}`}>
            <div className="avatar">
              {msg.sender === "bot" ? <Bot size={20} /> : <User size={20} />}
            </div>
            <div className="message-bubble">{msg.text}</div>
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>

      <div className="controls">
        <button
          className={`mic-button ${isRecording ? "recording" : ""}`}
          onMouseDown={startRecording}
          onMouseUp={stopRecording}
          onTouchStart={startRecording}
          onTouchEnd={stopRecording}
        >
          {isRecording ? <Square size={28} /> : <Mic size={28} />}
        </button>
        <p className="instruction">
          {isRecording ? "Release to Send" : "Hold to Speak"}
        </p>
      </div>
    </div>
  );
}