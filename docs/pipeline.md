# Meridian Pipeline

Meridian answers new-hire questions strictly from 5 loaded policy PDFs and backs every answer with verified citations. The backend does two separate jobs, and a React frontend sits on top of the API.

## Job 1: Ingestion (run once, offline)

Script: `ingest.py` (like an `npm run seed` script)

```
PDFs -> pages -> chunks -> embeddings -> Chroma
```

| Step | What happens | Why |
|---|---|---|
| Load | `pypdf` reads each PDF page by page and `clean_page_text` tidies the text | Keeps the page number for citations |
| Chunk | `RecursiveCharacterTextSplitter`, 1000 chars, 150 overlap | A whole PDF is too big and blurs meaning; overlap stops sentences being cut in half |
| Embed | `text-embedding-3-small` (1536 dims) | Turns text into vectors so similar meaning lands close together |
| Store | Chroma `PersistentClient` in `chroma_db/` (embedded, in-process) | The old collection is deleted first, so re-running never duplicates |

Result: 23 pages -> 28 chunks in the `tradewind_policies` collection, each with `source` (filename) and `page` (1-based) metadata.

## Job 2: Answering (every question)

Module: `rag.py`, called by `POST /api/ask` in `app.py` (the service module behind an Express route)

```
question
   |
   v
1. RETRIEVE   embed question -> Chroma returns the TOP_K nearest chunks
   |
   v
2. GENERATE   system prompt (rules) + user message (excerpts + question)
   |          -> chat model returns a structured object
   v
3. VERIFY     check every quote against the retrieved chunk text,
   |          group quotes per source, renumber markers
   v
JSON response: normal answer card OR not-found card
```

### 1. Retrieve
- Embed the question and ask Chroma for the `TOP_K` closest chunks (`TOP_K` lives in `config.py`).
- Chroma always returns the k nearest chunks, so empty results never mean "not found". Closeness measures topic, not whether the answer exists.
- An optional, lenient distance cutoff (about 1.5, to be tuned) would only remove obvious junk (not implemented yet).

### 2. Generate
- **System message** = `SYSTEM_PROMPT` from `prompts.py`, a constant made of three parts: `GROUNDING_RULES`, `INJECTION_DEFENSE`, `OUTPUT_FORMAT`.
- **User message** = the retrieved chunks wrapped in `<excerpts>` and `<excerpt id="1" source="..." page="...">` tags, plus the question.
- Document text never enters the system message, so untrusted text cannot sit in the channel that holds the rules.
- The model returns a Pydantic object via `with_structured_output(..., method="json_schema", strict=True)`. The `Field` descriptions are sent to the model with the schema, so they double as instructions:

```python
class Citation(BaseModel):
    excerpt_id: int   # must equal the [n] marker in the answer that this quote supports
    quote: str        # short verbatim quote copied from that excerpt

class MeridianAnswer(BaseModel):
    found: bool
    answer: str       # text with [n] markers, where n is the excerpt's own id
    citations: list[Citation]
```

- `temperature` is not passed: gpt-5.6 models only accept the default, and langchain-openai omits it anyway. Because of that, output varies between runs, so code must never depend on the model's exact behavior.
- The model returns only `excerpt_id` and `quote`. Code looks up filename and page from chunk metadata, so the model cannot invent them.

### 3. Verify and shape the response
- Collapse whitespace on both the quote and the chunk text, then check the quote is a substring of the exact chunk the model named. Out-of-range excerpt ids are ignored.
- Failed quotes are dropped. Surviving quotes are grouped by excerpt, so one source card can hold several stacked quotes.
- Markers are renumbered by order of first appearance (`[3]` becomes `[1]`), and markers with no verified quote are removed.
- If no marker survives, the answer is treated as not found, even when the model said `found=True`. An unverifiable answer never reaches the user.
- Filename and page always come from chunk metadata, never from the model.

### Known assumption: marker number == excerpt id

`renumber_markers` looks up each `[n]` in the dictionary of verified quotes, which is keyed by **excerpt id**. So it assumes the number in a marker is the id of the excerpt the claim came from.

**Bug this caused (found during frontend testing):** three valid questions about vacation and sick days all returned NOT FOUND. `try_debug.py` showed `found=True` and every quote verified under `excerpt_id=4`, but the model had numbered its markers like footnotes (`[1] [1] [1]`). Marker 1 was not in the verified dictionary, so every marker was stripped, no citation survived, and the not-found rule above fired. The safety net behaved correctly; its input broke the assumption. Earlier test runs passed only because the model happened to follow the convention.

**Layer 1 fix (applied):** the schema `Field` descriptions now state the rule explicitly (markers use the excerpt's own id; the quote's `excerpt_id` must equal the marker it supports; never renumber). One run after the fix was correct (`[4]` and `[1]` renumbered to `[1]` and `[2]`). Stability across many runs is still being checked.

**Layer 2 fallback (only if layer 1 proves unreliable):** add a `marker` number to each `Citation` and map markers to excerpts directly in code, so correctness no longer depends on the model matching ids. A prompt can reduce a behavior but cannot guarantee it, so anything that must always hold belongs in code.

## Found vs not found

The LLM decides via the `found` field. There are only two UI states:

| State | When |
|---|---|
| Answer card with citation badges and expandable source cards | An excerpt states a rule that applies, including a default when the question falls outside a closed exception list (the answer says plainly that the policy does not name the specific case) |
| Not-found card ("NOT FOUND IN DOCUMENTS", pale blue-gray with an info icon) | No excerpt contains an applicable rule, or no quote survived verification. No stretching a rule about a different topic by analogy |

The not-found sentence is a fixed constant (`NOT_FOUND_MESSAGE` in `config.py`), not the model's wording, which varies between runs.

## API

`POST /api/ask` with body `{"question": "..."}`

| Status | Meaning |
|---|---|
| 200 | `{found, answer, sources: [{number, source, page, quotes}]}`. `found: false` is the not-found state |
| 400 | Missing, blank, or over-500-character question (detailed developer-facing message; the UI blocks blank input so users should not see it) |
| 500 | Unexpected failure (generic message; details only in the server log) |

CORS allows only the React dev server origin (`http://localhost:5173`).

## Frontend

Vite + React (plain JS/JSX) with plain CSS files. Layout under `frontend/src/`:

| Folder / file | Role |
|---|---|
| `utilities/api.js` | `askQuestion()`: the one function that calls `POST /api/ask`. `fetch` does not throw on 400/500, so it checks `response.ok` itself and throws a readable error for network failures and API errors |
| `pages/Dashboard.jsx` | Owns the chat state (`messages`, `isLoading`) and composes the components |
| `components/Sidebar.jsx` | Company header, logo, grounding note, document list, footer |
| `components/ChatInput.jsx` | Controlled input; send is disabled for blank input and while a request is in flight |
| `css/theme.css` | Design tokens (colors, radii, font) as CSS variables; every other stylesheet reads them |

- **Theme:** blue on cool white (taken from the final mockup), with the Inter font.
- **State updates** always build a new array (`[...prev, item]`) because React detects changes by reference.
- **Built so far:** sidebar, chat input, and the request round trip with plain-text rendering. **In progress:** answer card with clickable citation badges, accordion source cards (with stacked quotes and `#page=N` links), not-found card, starter question pills, and the mobile drawer.

## Security

- Document text is untrusted data, never instructions (`INJECTION_DEFENSE`).
- Chroma runs embedded in-process only. Never run a Chroma HTTP or Docker server or expose a Chroma port (CVE-2026-45829 affects chromadb 1.0.0-1.5.9; pinned at 1.5.9). Check for a patched release before the project is finished.
- Policy PDFs are served as static files from the frontend (`frontend/public/docs/`) so users can open a cited source and verify it themselves. This is intentional because the documents are fictional. A real deployment with confidential policies would serve them behind authentication instead.
- Local demo only: there is no rate limiting. Before any public deployment, add rate limiting (Flask-Limiter) and set a spending cap in the OpenAI dashboard.
- Limitation: verification proves a quote exists in a retrieved chunk, not that the chunk is trustworthy. A fake rule planted in a document cannot be detected, so control over which documents are ingested is part of the security model.

## Test set

- **IN:** vacation, hotel (both $220 and the four-city $320 exception), 401(k) (all three facts), mileage, sick days, learning budget, Tokyo hotel (default handling). Sick days and vacation are the regression cases for the marker bug above.
- **OUT:** gym, dog in office, capital of France
- **Injection:** poisoned excerpts (a command to override the rules, and a fake system-prompt request) both returned not found with no leaked prompt
- Because output varies between runs, the whole set should be re-run several times, not once.

## Files

| File | Role |
|---|---|
| `backend/config.py` | Paths, model names, collection name, `TOP_K`, `NOT_FOUND_MESSAGE` |
| `backend/prompts.py` | `SYSTEM_PROMPT` |
| `backend/ingest.py` | Job 1 |
| `backend/rag.py` | Job 2: retrieve, generate, verify, renumber, `ask()` |
| `backend/app.py` | Flask `POST /api/ask` |
| `backend/try_search.py` | Retrieval testing script |
| `backend/try_ask.py` | End-to-end test of `ask()` on the IN/OUT set |
| `backend/try_inject.py` | Prompt-injection test with poisoned excerpts |
| `backend/try_debug.py` | Prints every stage for one question (retrieved chunks, model output, verified quotes, renumbered result) |
| `backend/docs/` | Source PDFs for ingestion (source of truth) |
| `frontend/public/docs/` | Served copies of the PDFs for the sidebar links (re-copy after any PDF change) |