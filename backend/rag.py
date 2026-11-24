# --- stdlib ---
import re

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


from config import CHAT_MODEL, CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL, TOP_K
from prompts import SYSTEM_PROMPT

load_dotenv()

# Pydantic Shaping / Schema Modeling

class Citation(BaseModel):
    excerpt_id: int = Field(description="The id of the excerpt the quote was copied from.")
    quote: str = Field(description="A short verbatim quote copied exactly from that excerpt.")

class MeridianAnswer(BaseModel):
    found: bool = Field(description="True only if an excerpt states a rule that answers the question.")
    answer: str = Field(description="The answer with [1], [2] markers, or one short not-found sentence.")
    citations: list[Citation] = Field(description="One entry per marker used. Empty if found is false.")


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

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()