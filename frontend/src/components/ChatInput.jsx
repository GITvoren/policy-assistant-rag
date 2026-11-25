import { useState } from "react";

import "../css/chat-input.css";

export default function ChatInput({ onSend, disabled }) {
  const [value, setValue] = useState("");
  const canSend = value.trim() !== "" && !disabled;

  function handleSubmit(event) {
    event.preventDefault();
    if (!canSend) return;
    onSend(value.trim());
    setValue("");
  }

  return (
    <form className="chat-input" onSubmit={handleSubmit}>
      <input
        className="chat-input__field"
        type="text"
        value={value}
        onChange={(event) => setValue(event.target.value)}
        placeholder="Ask about policies, benefits, or onboarding"
        maxLength={500}
      />
      <button
        className="chat-input__send"
        type="submit"
        disabled={!canSend}
        aria-label="Send question"
      >
        →
      </button>
    </form>
  );
}