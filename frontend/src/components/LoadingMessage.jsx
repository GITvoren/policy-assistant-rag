import "../css/loading-message.css";

export default function LoadingMessage() {
  return (
    <div className="loading-message" role="status" aria-label="Meridian is thinking">
      <span className="loading-message__dot" />
      <span className="loading-message__dot" />
      <span className="loading-message__dot" />
    </div>
  );
}