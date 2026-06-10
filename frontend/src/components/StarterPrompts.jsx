import React from "react";

export default function StarterPrompts({ prompts, onPromptClick, disabled }) {
  return (
    <div className="starter-prompts">
      {prompts.map((prompt) => (
        <button
          key={prompt}
          className="starter-prompt"
          onClick={() => onPromptClick(prompt)}
          disabled={disabled}
        >
          {prompt}
        </button>
      ))}
    </div>
  );
}