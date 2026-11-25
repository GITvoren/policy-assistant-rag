import "../css/sidebar.css";

const LOGO_SRC = "/images/brand-logo.png";

const DOCUMENTS = [
  { name: "Employee-Handbook.pdf", pages: 8 },
  { name: "PTO-Policy.pdf", pages: 4 },
  { name: "Expense-Policy.pdf", pages: 4 },
  { name: "IT-Security-Policy.pdf", pages: 4 },
  { name: "Onboarding-Checklist.pdf", pages: 3 },
];

export default function Sidebar({ isOpen, onClose }) {
  return (
    <aside className={`sidebar ${isOpen ? "sidebar--open" : ""}`}>
      <button
        type="button"
        className="sidebar__close"
        onClick={onClose}
        aria-label="Close documents"
      >
        ×
      </button>
      <p className="sidebar__company">Tradewind Global, Inc.</p>

      <h1 className="sidebar__brand">
        <img className="sidebar__logo" src={LOGO_SRC} alt="Meridian" />
      </h1>

      <p className="sidebar__tagline">Policy &amp; onboarding assistant</p>
      <hr className="sidebar__divider" />

      <p className="sidebar__note">
        Meridian answers based on the documents below. If the information isn&apos;t covered, it lets you know.
      </p>

      <h2 className="sidebar__label">
        Knowledge base · {DOCUMENTS.length} documents
      </h2>
      <p className="sidebar__hint">
        Open any document to verify Meridian&apos;s answers. Public for <em>demo purposes</em> only.
      </p>

      <ul className="sidebar__docs">
        {DOCUMENTS.map((doc) => (
          <li key={doc.name}>
            <a
              className="sidebar__doc"
              href={`/docs/${encodeURIComponent(doc.name)}`}
              target="_blank"
              rel="noopener noreferrer"
            >
              <span className="pdf-icon" aria-hidden="true">
                <img src="/images/pdf-icon.png" alt="" />
              </span>
              <span className="sidebar__doc-name">{doc.name}</span>
              <span className="sidebar__pages">{doc.pages} pgs</span>
            </a>
          </li>
        ))}
      </ul>

      <p className="sidebar__footer">
        Portfolio demo. All documents are fictional.
      </p>
    </aside>
  );
}