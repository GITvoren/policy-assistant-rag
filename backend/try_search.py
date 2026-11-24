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
    for doc in vectorstore.similarity_search(question, k=3):
        print("  ", doc.metadata, repr(doc.page_content[:70]))
        
gym_top = vectorstore.similarity_search("Does the company reimburse my gym membership?", k=1)[0]
print("\n--- Full top gym chunk ---")
print(gym_top.page_content)