import React, { useCallback } from "react";

export default function InputBox({ value, onChange, onSend, disabled, canSend }) {
  const handleKeyDown = useCallback(
    (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        if (canSend) {
          onSend();
        }
      }
    },
    [canSend, onSend]
  );

  return (
    <div className="input-box">
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask about projects, background, technical strengths, or current focus..."
        rows={3}
        disabled={disabled}
      />
      <button onClick={onSend} disabled={!canSend}>
        Send
      </button>
    </div>
  );
}