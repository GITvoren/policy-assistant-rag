import "../css/usermessage.css";

export default function UserMessage({ text }) {
  return (
    <div className="user-message">
      <p className="user-message__text">{text}</p>
    </div>
  );
}