from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
CHROMA_DIR = BASE_DIR / "chroma_db"

BOT_NAME = "Meridian"
COMPANY_NAME = "Tradewind Global, Inc."

CHAT_MODEL = "gpt-5.6-luna"
EMBEDDING_MODEL = "text-embedding-3-small"
COLLECTION_NAME = "tradewind_policies"

TOP_K = 4

NOT_FOUND_MESSAGE = "This isn't covered in the Tradewind policy documents I have."