import "../css/starter-questions.css";

const QUESTIONS = [
  "What do I do in week one?",
  "Can I use my personal laptop?",
  "How do I file an expense?",
  "How many vacation leaves do I get?",
  "What are the benefits?"
];

export default function StarterQuestions({ onPick, disabled }) {
  return (
    <div className="starter-questions">
      {QUESTIONS.map((question) => (
        <button
          key={question}
          type="button"
          className="starter-questions__pill"
          onClick={() => onPick(question)}
          disabled={disabled}
        >
          {question}
        </button>
      ))}
    </div>
  );
}