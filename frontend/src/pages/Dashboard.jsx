import { useEffect, useRef, useState } from "react";

import "../css/dashboard.css";
import AnswerCard from "../components/AnswerCard";
import ChatInput from "../components/ChatInput";
import NotFound from "../components/NotFound";
import Sidebar from "../components/Sidebar";
import SourceCard from "../components/SourceCard";
import UserMessage from "../components/UserMessage";
import { askQuestion } from "../utilities/api";
import ErrorMessage from "../components/ErrorMessage";
import LoadingMessage from "../components/LoadingMessage";

export default function Dashboard() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

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
          {messages.map((message) => {
            if (message.role === "assistant") {
              if (!message.result.found) {
                return (
                  <NotFound
                    key={message.id}
                    message={message.result.answer}
                  />
                );
              }
              return (
                <div key={message.id} className="assistant-message">
                  <AnswerCard answer={message.result.answer} />
                  {message.result.sources.map((source) => (
                    <SourceCard key={source.number} source={source} />
                  ))}
                </div>
              );
            }
            if (message.role === "user") {
              return <UserMessage key={message.id} text={message.text} />;
            }
            return <ErrorMessage key={message.id} message={message.text} />;
                      })}
          {isLoading && <LoadingMessage />}
          <div ref={bottomRef} />
        </div>
        <ChatInput onSend={handleSend} disabled={isLoading} />
      </main>
    </div>
  );
}