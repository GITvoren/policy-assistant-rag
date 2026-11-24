# --- stdlib ---
import re

# --- third-party ---
import chromadb
from chromadb.errors import NotFoundError
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

# --- local ---
from config import CHROMA_DIR, COLLECTION_NAME, DOCS_DIR, EMBEDDING_MODEL

load_dotenv()

HEADER_RE = re.compile(
    r"^Tradewind Global, Inc\.\s*\|.*?\|\s*Confidential\s*\nPage \d+\s*\n"
)


# Load + Clean
def clean_page_text(text: str) -> str: # type hint. meaning: takes a string, returns a string (optional)
    text = HEADER_RE.sub("", text, count=1)   # drop header + "Page N" line
    text = text.replace("\x7f", "-")          # fix bullet glyph
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    return "\n".join(lines).strip()

def load_pages() -> list[Document]: # returns a list(array in js) of the pages of the pdf
    pages = []
    for pdf_path in sorted(DOCS_DIR.glob("*.pdf")):
        reader = PdfReader(pdf_path)
        for page_number, page in enumerate(reader.pages, start=1):
            text = clean_page_text(page.extract_text() or "")
            assert "\x7f" not in text
            pages.append(
                Document(
                    page_content=text,
                    metadata={"source": pdf_path.name, "page": page_number}, # for citation
                )
            )
    return pages

# Chunking
def split_pages(pages: list[Document]) -> list[Document]: #takes list of pages, returns list of splitted pages(chunks)
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    return splitter.split_documents(pages)


# embedding (chunks -> vector) and storing of vectors in vector db
def store_chunks(chunks: list[Document]) -> None: #chunks in, nothing out.(vectors stay in vector database)
     
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    # Start fresh every run so re-running never creates duplicates
    try:
        client.delete_collection(COLLECTION_NAME)
    except NotFoundError:
        pass  # first run: nothing to delete yet

    vectorstore = Chroma(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding_function=OpenAIEmbeddings(model=EMBEDDING_MODEL),
    )
    vectorstore.add_documents(chunks) # this is where embedding happens

    count = client.get_collection(COLLECTION_NAME).count()
    print(f"Stored {count} chunks in Chroma")




if __name__ == "__main__":
    pages = load_pages()
    chunks = split_pages(pages)
    print(f"{len(pages)} pages -> {len(chunks)} chunks")
    store_chunks(chunks)