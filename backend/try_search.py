import chromadb
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from config import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL

load_dotenv()

vectorstore = Chroma(
    client=chromadb.PersistentClient(path=str(CHROMA_DIR)),
    collection_name=COLLECTION_NAME,
    embedding_function=OpenAIEmbeddings(model=EMBEDDING_MODEL),
)

for question in [
    "How many vacation days do I get?",
    "What is the maximum amount I can spend on a hotel?",
    "Does the company reimburse my gym membership?",
]:
    print(f"\n{question}")
    for doc, score in vectorstore.similarity_search_with_score(question, k=3):
        print(f"  {score:.3f}", doc.metadata, repr(doc.page_content[:70]))

gym_top = vectorstore.similarity_search("Does the company reimburse my gym membership?", k=1)[0]
print("\n--- Full top gym chunk ---")
print(gym_top.page_content)

hotel_results = vectorstore.similarity_search(
    "What is the maximum amount I can spend on a hotel?", k=1
)
print("\n--- Full top hotel chunk ---")
print(hotel_results[0].page_content)

tests = [
    ("IN", "How many sick days do I get?"),
    ("IN", "How much is the learning budget?"),
    ("IN", "How much am I reimbursed per mile for using my own car?"),
    ("OUT", "Does the company offer a 401(k) match?"),
    ("OUT", "Can I bring my dog to the office?"),
    ("OUT", "What is the capital of France?"),
]

print("\n--- Best score per question ---")
for label, question in tests:
    _, score = vectorstore.similarity_search_with_score(question, k=1)[0]
    print(f"{label:4} {score:.3f}  {question}")


top = vectorstore.similarity_search("Does the company offer a 401(k) match?", k=1)[0]
print("\n--- Top 401(k) chunk ---")
print(top.metadata)
print(top.page_content)