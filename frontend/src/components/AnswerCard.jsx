import "../css/answercard.css"

export default function AnswerCard({ answer }) {
  const pieces = answer.split(/\[(\d+)\]/);

  function renderBold(text) {
  return text.split(/\*\*(.+?)\*\*/g).map((part, index) =>
    index % 2 === 1 ? <strong key={index}>{part}</strong> : part
  );
}

  return (
    <div className="answer-card">
      <p className="answer-card__text">
        {pieces.map((piece, index) =>
          index % 2 === 1 ? (
            <button key={index} type="button" className="answer-card__marker">
              [{piece}]
            </button>
          ) : (
            <span key={index}>{renderBold(piece)}</span>
          )
        )}
      </p>
    </div>
  );
}