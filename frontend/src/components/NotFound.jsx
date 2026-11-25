import "../css/not-found-card.css";

export default function NotFoundCard({ message }) {
  return (
    <div className="not-found-card">
      <div className="not-found-card__header">
        <span className="not-found-card__icon" aria-hidden="true">i</span>
        <p className="not-found-card__label">Not found in documents</p>
      </div>
      <p className="not-found-card__text">{message}</p>
    </div>
  );
}