import { useState } from "react";

import "../css/dashboard.css";
import ChatInput from "../components/ChatInput";
import Sidebar from "../components/Sidebar";
import { askQuestion } from "../utilities/api";

export default function Dashboard() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  async function handleSend(question) {
    setMessages((prev) => [
      ...prev,
      { id: crypto.randomUUID(), role: "user", text: question },
    ]);
    setIsLoading(true);

    try {
      const result = await askQuestion(question);
      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: "assistant", result },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: "error", text: error.message },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="dashboard">
      <Sidebar />
      <main className="dashboard__main">
        <div className="dashboard__messages">
          {messages.map((message) => (
            <p key={message.id}>
              {message.role}:{" "}
              {message.role === "assistant" ? message.result.answer : message.text}
            </p>
          ))}
          {isLoading && <p>Thinking…</p>}
        </div>
        <ChatInput onSend={handleSend} disabled={isLoading} />
      </main>
    </div>
  );
}