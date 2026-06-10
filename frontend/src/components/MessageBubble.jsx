import React from "react";
import SourcePanel from "./SourcePanel.jsx";
import DebugDrawer from "./DebugDrawer.jsx";

export default function MessageBubble({ message }) {
  const isAssistant = message.role === "assistant";

  return (
    <div className={`message-row ${message.role}`}>
      <div className={`message-bubble ${message.role}`}>
        <div className="message-text">{message.text}</div>

        {isAssistant && typeof message.confidence === "number" ? (
          <div className="confidence-pill">Confidence: {message.confidence.toFixed(2)}</div>
        ) : null}

        {isAssistant && message.sources?.length ? (
          <SourcePanel sources={message.sources} />
        ) : null}

        {isAssistant && message.debug ? <DebugDrawer debug={message.debug} /> : null}
      </div>
    </div>
  );
}