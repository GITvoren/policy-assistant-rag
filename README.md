
# Meridian: Retrieval-Augmented Generation (RAG) Policy Assistant

**Retrieval-Augmented Generation (RAG) · LLM Integration · Vector Database Architecture · Verified AI Citations**

Meridian is an AI-powered policy and onboarding assistant built using a **Retrieval-Augmented Generation (RAG) architecture**. It integrates large language models with semantic search and Chroma vector storage to retrieve relevant information from policy documents and generate context-aware answers grounded in source material.

Built with **Python, LangChain, OpenAI, and ChromaDB**, Meridian features a document ingestion pipeline, embedding generation, semantic retrieval, structured LLM responses, and programmatic citation verification to ensure answers remain traceable to their original sources.

Rather than relying on the language model's general knowledge, Meridian answers exclusively from five loaded policy PDFs. Every response includes numbered citations linked to source cards containing the original filename, page number, and verified document excerpts. When relevant information cannot be found, the system explicitly indicates that instead of generating an unsupported answer.

> Portfolio demo. All documents are fictional.

[Live Demo](https://meridian-policy-assistant.vercel.app/)



## Why it exists

A wrong answer about pay, leave or expenses is worse than no answer. Language models can sound confident while being wrong, so Meridian does not ask you to trust the model:

- The model must back every claim with a quote from a retrieved excerpt.
- **Code**, not the model, verifies that each quote appears in the excerpt it claims to come from. Quotes that fail are dropped.
- Filename and page numbers come from stored document metadata, never from the model.
- If no citation survives verification, the user sees the "not found" state instead of an unverifiable answer.
- Document text is treated strictly as untrusted data, never as instructions.

## Features

- Answers with inline citation markers ([1], [2]) that match expandable source cards
- Several verified quotes can be stacked inside one source card
- Key facts in an answer can appear in bold (the app renders a single `**bold**` pattern itself, with no markdown library)
- A distinct "not found in documents" state
- Starter question pills in a sideways-scrolling row
- Loading and error states
- Clickable document list that opens the source PDF, so users can check answers themselves
- Responsive layout: on phones the sidebar becomes a slide-in drawer opened from a "5 docs" button
- Prompt-injection defenses, tested with poisoned excerpts
- Input validation and a generic error message for unexpected failures

## Tech stack

| Layer | Tools |
|---|---|
| Backend | Python 3.12, Flask, flask-cors |
| AI | LangChain (`langchain-openai`, `langchain-chroma`, `langchain-text-splitters`), OpenAI chat model `gpt-5.6-luna`, embeddings `text-embedding-3-small`, Pydantic structured output |
| Vector store | Chroma, embedded and persistent (runs in-process) |
| PDF reading | pypdf |
| Frontend | Vite, React (plain JS/JSX), plain CSS with CSS variables |

## How it works

```
question -> embed -> nearest chunks (Chroma) -> chat model (structured output)
         -> verify quotes in code -> renumber markers -> JSON -> React
```

The full walkthrough, including design decisions and a bug write-up, is in [docs/pipeline.md](docs/pipeline.md).

## Getting started

### Prerequisites

- Python 3.12
- Node.js (current LTS)
- An OpenAI API key

### 1. Backend

From the repo root, in Git Bash (on macOS/Linux, activate with `source venv/bin/activate` instead):

```bash
cd backend
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```

Create `backend/.env` with your key:

```
OPENAI_API_KEY=your-key-here
```

Build the knowledge base (run once, and again whenever the PDFs change):

```bash
python ingest.py
```

Start the API:

```bash
python app.py
```

It listens on `http://127.0.0.1:5000`.

### 2. Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The backend only accepts requests from that origin.

### 3. Try the API without the UI

```bash
curl -X POST http://127.0.0.1:5000/api/ask -H "Content-Type: application/json" -d '{"question": "How much can I spend on a hotel?"}'
```

## API

`POST /api/ask` with body `{"question": "..."}`

| Status | Meaning |
|---|---|
| 200 | `{found, answer, sources: [{number, source, page, quotes}]}`. `found: false` is the not-found state |
| 400 | Missing, blank, or over-500-character question |
| 500 | Unexpected failure (generic message; details only in the server log) |

## Testing

There is no formal test suite yet. These scripts in `backend/` act as manual checks:

| Script | What it checks |
|---|---|
| `try_ask.py` | Questions that should be answered and questions that should be not found, run through `ask()` |
| `try_inject.py` | Prompt-injection attempts hidden in fake excerpts |
| `try_debug.py` | Prints every stage (retrieval, model output, verification) for one question. Pass the question as an argument, for example `python try_debug.py "How many sick days per month?"` |

The model can't be given a temperature, so its output varies between runs. Run the question set several times, not once. A quick repeat loop in Git Bash (`-a` stops grep treating the output as binary when it contains special characters):

```bash
for i in 1 2 3 4 5; do python try_debug.py "How many vacations leave do we have?" | grep -a renumbered; done
```

## Project structure

```
policy-assistant-rag/
├── backend/
│   ├── docs/            source PDFs for ingestion
│   ├── chroma_db/       local vector store (generated, not committed)
│   ├── config.py        paths, model names, TOP_K, fixed not-found message
│   ├── prompts.py       system prompt
│   ├── ingest.py        PDFs -> chunks -> embeddings -> Chroma
│   ├── rag.py           retrieve, generate, verify, renumber, ask()
│   ├── app.py           Flask API
│   └── try_*.py         manual test scripts
├── frontend/
│   ├── public/docs/     served copies of the PDFs
│   └── src/             components, pages, css, utilities
└── docs/
    └── pipeline.md      how the pipeline works
```

## Status

- **Backend:** complete and tested, including a repeated-run check of the citation-marker fix. Flask-Limiter rate limiting, and OpenAI API spend caps.
- **Frontend:** complete. Chat flow, answer and source cards, not-found card, starter questions, loading and error states, and the mobile layout are all working.
- **Hosting** complete. Frontend deployed on Vercel and backend deployed on Railway.

## Limitations

- **Verification checks that a quote exists, not that it is true.** A fake rule planted in a document can't be detected, so control over which documents get ingested is part of the security model. It also checks quotes, not every claim in the answer text.
- **Output varies between runs.** The chat model does not accept a custom temperature, so important guarantees live in code, and the question set should be run repeatedly.
- **No memory between questions.** Each question is answered on its own, so a follow-up like "and what about part-time?" won't work. Chat history lives only in the browser tab and is cleared on refresh.
- **Greetings and small talk show the not-found card.** The app has two states only (a cited answer or not found), on purpose, so everything goes through the strict "only from the documents" path.
- **No rate limiting or authentication.** This was built as a local demo. Before any public deployment, add rate limiting (for example Flask-Limiter), set a spending cap in the OpenAI dashboard, turn off Flask debug mode, and serve confidential documents behind authentication.
- **The policy PDFs are served publicly from the frontend on purpose**, so users can verify answers. That is fine only because the documents are fictional.
- **Chunk size (1000, overlap 150) and `TOP_K` (4) are starting values.** Multi-part questions may need tuning.
- **Flask's development server is not built for real traffic.**

## Security notes

- Chroma runs embedded in the Flask process only. Never run a Chroma HTTP or Docker server or expose a Chroma port: chromadb 1.0.0 to 1.5.9 is affected by CVE-2026-45829. This project pins chromadb 1.5.9 and should be re-checked for a patched release.
- Keep `.env` out of version control.

## Built with AI assistance

This is a learning project. I built it step by step with Claude Chat as a tutor and pair programmer, running and testing each part myself, and I can walk through every piece of it.