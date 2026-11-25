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
import StarterQuestions from "../components/StarterQuestions";

export default function Dashboard() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

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
      <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />
      {isSidebarOpen && (
        <div
          className="dashboard__backdrop"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}
      <main className="dashboard__main">
        <header className="mobile-header">
          <div>
            <p className="mobile-header__company">Tradewind Global, Inc.</p>
            <p className="mobile-header__title">
              <strong>Meridian</strong> Policy Assistant
            </p>
          </div>
          <button
            type="button"
            className="dashboard__docs-button"
            onClick={() => setIsSidebarOpen(true)}
          >
            5 docs
          </button>
        </header>
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
        <StarterQuestions onPick={handleSend} disabled={isLoading} />
        <ChatInput onSend={handleSend} disabled={isLoading} />
      </main>
    </div>
  );
}