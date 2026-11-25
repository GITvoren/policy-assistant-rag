# --- stdlib ---
import re

# --- third-party ---
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel, Field

# --- local ---
from config import (
    CHAT_MODEL,
    CHROMA_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    NOT_FOUND_MESSAGE,
    TOP_K,
)

from prompts import SYSTEM_PROMPT

load_dotenv()

# Pydantic Shaping / Schema Modeling


class Citation(BaseModel):
    excerpt_id: int = Field(
        description="The id of the excerpt the quote was copied from. "
        "Must equal the [n] marker in the answer that this quote supports."
    )
    quote: str = Field(description="A short verbatim quote copied exactly from that excerpt.")

class MeridianAnswer(BaseModel):
    found: bool = Field(description="True only if an excerpt states a rule that answers the question.")
    answer: str = Field(
        description="The answer with [n] markers, where n is the id of the excerpt "
        "the claim comes from. Use the excerpt's own id; never renumber. "
        "Or one short not-found sentence."
    )
    citations: list[Citation] = Field(description="One entry per quote used. Empty if found is false.")


vectorstore = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=OpenAIEmbeddings(model=EMBEDDING_MODEL),
    persist_directory=str(CHROMA_DIR),
)


def retrieve(question: str) -> list[tuple[Document, float]]: # question in(string), list of tuples out (top chunks, score)
    return vectorstore.similarity_search_with_score(question, k=TOP_K)

# python -c "from rag import retrieve; [print(round(s, 3), d.metadata) for d, s in retrieve('How much can I spend on a hotel?')]"



# def build_user_message(question, results):
# generate blocks to be fed to openai api
def build_user_message(question: str, results: list[tuple[Document, float]]) -> str: # question + chunks in, string out
    blocks: list[str] = [] # blocks = []  -- type hint string
    for i, (doc, _score) in enumerate(results, start=1):  # gives each chunk an id(for excerpt_id)
        source = doc.metadata["source"]
        page = doc.metadata["page"]
        blocks.append(  # blocks == structured chunk + question
            f'<excerpt id="{i}" source="{source}" page="{page}">\n'
            f"{doc.page_content}\n"
            f"</excerpt>"
        )
    excerpts = "\n".join(blocks)
    return f"<excerpts>\n{excerpts}\n</excerpts>\n\nQuestion: {question}"

# python -c "from rag import retrieve, build_user_message, generate; q = 'How much can I spend on a hotel?'; r = generate(build_user_message(q, retrieve(q))); print(r.found); print(r.answer); print(r.citations)"


# Enforce the MeridianAnswer Pydantic schema on the LLM's output
llm = ChatOpenAI(model=CHAT_MODEL)
structured_llm = llm.with_structured_output(MeridianAnswer, method="json_schema", strict=True)

def generate(user_message: str) -> MeridianAnswer: # system prompt + blocks in, shaped output with citations and bool out
    return structured_llm.invoke(
        [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user_message)]
    )

#strip whitespace
def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

# fix citation bool going true on empty string
# hallucination guardrail
def quote_is_verbatim(quote: str, chunk_text: str) -> bool:
    clean_quote = normalize(quote)
    if not clean_quote:
        return False
    return clean_quote in normalize(chunk_text)

# python -c "from rag import quote_is_verbatim as v; print(v('per night', 'limit is 320 per\nnight.')); print(v('per day', 'limit is 320 per\nnight.')); print(v('   ', 'anything'))"


# Keep only citations whose quote appears verbatim in the cited chunk, grouped by excerpt
def verify_citations(
    answer: MeridianAnswer, results: list[tuple[Document, float]]
) -> dict[int, list[str]]:
    verified: dict[int, list[str]] = {}
    for citation in answer.citations:
        if not 1 <= citation.excerpt_id <= len(results):
            continue
        chunk = results[citation.excerpt_id - 1][0]
        if not quote_is_verbatim(citation.quote, chunk.page_content):
            continue
        quotes = verified.setdefault(citation.excerpt_id, [])
        clean_quote = normalize(citation.quote)
        if clean_quote not in quotes:
            quotes.append(clean_quote)
    return verified

# Renumber [n] markers by order of first appearance; drop markers with no verified quote.
# Returns the new text and the old excerpt ids in their new order (order[0] is behind [1]).
def renumber_markers(
    answer_text: str, verified: dict[int, list[str]]
) -> tuple[str, list[int]]:
    order: list[int] = []

    def replace(match: re.Match[str]) -> str:
        space, old_id = match.group(1), int(match.group(2))
        if old_id not in verified:  # no verified quote: delete marker
            return ""
        if old_id not in order:
            order.append(old_id) # first time seen: remember it
        return f"{space}[{order.index(old_id) + 1}]" # new number = position in order

    new_text = re.sub(r"(\s?)\[(\d+)\]", replace, answer_text)
    return new_text.strip(), order


# Build the source-card data for the UI, in the new marker order
def build_sources(
    order: list[int],
    verified: dict[int, list[str]],
    results: list[tuple[Document, float]],
) -> list[dict]:
    sources: list[dict] = []
    for new_number, old_id in enumerate(order, start=1):
        chunk = results[old_id - 1][0]
        sources.append(
            {
                "number": new_number,
                "source": chunk.metadata["source"],
                "page": chunk.metadata["page"],
                "quotes": verified[old_id],
            }
        )
    return sources

# The one entry point the API calls: question in, plain dict out
def ask(question: str) -> dict:
    results = retrieve(question)
    answer = generate(build_user_message(question, results))

    if not answer.found:
        return {"found": False, "answer": NOT_FOUND_MESSAGE, "sources": []}

    verified = verify_citations(answer, results)
    text, order = renumber_markers(answer.answer, verified)

    if not order:
        return {"found": False, "answer": NOT_FOUND_MESSAGE, "sources": []}

    return {
        "found": True,
        "answer": text,
        "sources": build_sources(order, verified, results),
    }
