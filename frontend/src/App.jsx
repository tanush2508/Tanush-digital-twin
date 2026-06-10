import React, { useEffect, useMemo, useState } from "react";
import { getStatus, sendMessage } from "./api.js";
import ChatWindow from "./components/ChatWindow.jsx";
import InputBox from "./components/InputBox.jsx";
import StarterPrompts from "./components/StarterPrompts.jsx";
import StatusBar from "./components/StatusBar.jsx";

const STARTER_PROMPTS = [
  "What project best shows your production AI engineering skills?",
  "Tell me about RepaintWiz",
  "What are your technical strengths?",
  "What are you focused on right now?",
  "What were you working on recently?",
  "What is your favorite sports team?"
];

function makeId() {
  return `${Date.now()}-${Math.random()}`;
}

export default function App() {
  const [messages, setMessages] = useState([
    {
      id: makeId(),
      role: "assistant",
      text: "Hi, I’m Tanush’s digital twin. Ask me about my background, projects, technical strengths, or what I’m focused on right now.",
      sources: [],
      confidence: null,
      debug: null
    }
  ]);

  const [status, setStatus] = useState(null);
  const [input, setInput] = useState("");
  const [debugMode, setDebugMode] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadStatus() {
      try {
        const data = await getStatus();
        setStatus(data);
      } catch (err) {
        setError(err.message || "Failed to load backend status.");
      }
    }

    loadStatus();
  }, []);

  const canSend = useMemo(() => input.trim().length > 0 && !loading, [input, loading]);

  async function handleSend(customMessage) {
    const message = (customMessage ?? input).trim();
    if (!message || loading) {
      return;
    }

    setError("");
    setLoading(true);

    const userMessage = {
      id: makeId(),
      role: "user",
      text: message
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    try {
      const result = await sendMessage(message, debugMode);

      const assistantMessage = {
        id: makeId(),
        role: "assistant",
        text: result.answer,
        sources: result.sources ?? [],
        confidence: result.confidence ?? null,
        debug: result.debug ?? null
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setError(err.message || "Something went wrong while sending the message.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app-shell">
      <div className="app-container">
        <header className="app-header">
          <div>
            <p className="eyebrow">Personal project</p>
            <h1>Tanush Digital Twin</h1>
            <p className="subtext">
              A grounded professional twin with layered memory, source-backed responses, and a debug trace for evaluation.
            </p>
          </div>

          <label className="debug-toggle">
            <input
              type="checkbox"
              checked={debugMode}
              onChange={(e) => setDebugMode(e.target.checked)}
            />
            <span>Debug mode</span>
          </label>
        </header>

        <StatusBar status={status} />

        <StarterPrompts
          prompts={STARTER_PROMPTS}
          onPromptClick={handleSend}
          disabled={loading}
        />

        {error ? <div className="error-banner">{error}</div> : null}

        <ChatWindow messages={messages} loading={loading} />

        <InputBox
          value={input}
          onChange={setInput}
          onSend={() => handleSend()}
          disabled={loading}
          canSend={canSend}
        />
      </div>
    </div>
  );
}