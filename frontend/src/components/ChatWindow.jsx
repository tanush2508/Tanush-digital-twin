import React from "react";
import MessageBubble from "./MessageBubble.jsx";

export default function ChatWindow({ messages, loading }) {
  return (
    <div className="chat-window">
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}

      {loading ? (
        <div className="message-row assistant">
          <div className="message-bubble assistant loading-bubble">
            <div className="loading-dots">
              <span />
              <span />
              <span />
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}