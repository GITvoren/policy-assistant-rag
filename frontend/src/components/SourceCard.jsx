import { useRef, useState } from "react";

import "../css/sourcecard.css";

export default function SourceCard({ source }) {
  const [isOpen, setIsOpen] = useState(false);
  const cardRef = useRef(null);

function handleTransitionEnd(event) {
  if (isOpen && event.target === event.currentTarget) {
    cardRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }
}

  return (
    <div className="source-card" ref={cardRef}>
          <button
          type="button"
          className="source-card__header"
          onClick={() => setIsOpen((prev) => !prev)}
          aria-expanded={isOpen}
          >
          <span className="source-card__number">[{source.number}]</span>
          <span className="source-card__file">{source.source}</span>
          <span className="source-card__page">page {source.page}</span>
          <span className="source-card__chevron" aria-hidden="true" />
          </button>
          <div
          className={`source-card__body ${isOpen ? "source-card__body--open" : ""}`}
          aria-hidden={!isOpen}
          onTransitionEnd={handleTransitionEnd}
          >
               <div className="source-card__clip">
                    <div className="source-card__quotes">
                         {source.quotes.map((quote) => (
                         <blockquote key={quote} className="source-card__quote">
                              {quote}
                         </blockquote>
                         ))}
                    </div>
               </div>
          </div>
    </div>
  );
}