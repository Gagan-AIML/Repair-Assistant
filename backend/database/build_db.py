"""
build_db.py -- Build the ChromaDB vector store from all knowledge sources.
Run this once before starting app.py. Resumable: safely re-run after interruption.

Sources loaded:
  - data/          (PDF repair manuals)
  - knowledge/     (custom .txt repair knowledge files)
"""

import os
import sys
import time
import hashlib
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER   = os.path.join(BASE_DIR, "data")
KB_FOLDER     = os.path.join(BASE_DIR, "knowledge")
CHROMA_DB_DIR = os.path.join(BASE_DIR, "chroma_db")

BATCH_SIZE  = 40    # chunks per API call (safe under 100/min)
BATCH_DELAY = 70    # seconds between batches

# ─────────────────────────────────────────────
#  EMBEDDING MODEL
# ─────────────────────────────────────────────
print("[*] Initializing embedding model...")
embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

documents = []

# ─────────────────────────────────────────────
#  LOAD PDFs
# ─────────────────────────────────────────────
print(f"\n[PDF] Loading PDFs from: {DATA_FOLDER}")
if os.path.isdir(DATA_FOLDER):
    for file in os.listdir(DATA_FOLDER):
        if file.lower().endswith(".pdf"):
            path = os.path.join(DATA_FOLDER, file)
            print(f"   [OK] Loading PDF: {file}")
            try:
                loader = PyPDFLoader(path)
                docs = loader.load()
                documents.extend(docs)
                print(f"      -> {len(docs)} pages loaded")
            except Exception as e:
                print(f"      [WARN] Failed to load {file}: {e}")
else:
    print("   [WARN] data/ folder not found, skipping PDFs")

#  LOAD TXT KNOWLEDGE FILES
print(f"\n[KB] Loading knowledge files from: {KB_FOLDER}")
if os.path.isdir(KB_FOLDER):
    for file in os.listdir(KB_FOLDER):
        if file.lower().endswith(".txt"):
            path = os.path.join(KB_FOLDER, file)
            print(f"   [OK] Loading: {file}")
            try:
                loader = TextLoader(path, encoding="utf-8")
                docs = loader.load()
                documents.extend(docs)
                print(f"      -> {len(docs)} document(s) loaded")
            except Exception as e:
                print(f"      [WARN] Failed to load {file}: {e}")
else:
    print("   [WARN] knowledge/ folder not found, skipping .txt files")

if not documents:
    print("\n[ERROR] No documents loaded.")
    sys.exit(1)

print(f"\n[INFO] Total documents loaded: {len(documents)}")

# ─────────────────────────────────────────────
#  SPLIT INTO CHUNKS
# ─────────────────────────────────────────────
print("\n[*] Splitting documents into chunks...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150,
    separators=["\n\n", "\n", ".", " "]
)
split_docs = text_splitter.split_documents(documents)
print(f"   -> {len(split_docs)} chunks total")

# ─────────────────────────────────────────────
#  OPEN / CREATE CHROMA (resumable)
# ─────────────────────────────────────────────
print(f"\n[DB] Opening ChromaDB at: {CHROMA_DB_DIR}")
vectorstore = Chroma(
    persist_directory=CHROMA_DB_DIR,
    embedding_function=embedding_model
)

existing_count = vectorstore._collection.count()
print(f"   -> Already indexed: {existing_count} vectors")

# Generate deterministic IDs so we can detect what's already in the DB
def make_id(doc, idx):
    content_hash = hashlib.md5(doc.page_content.encode()).hexdigest()[:12]
    return f"doc_{idx}_{content_hash}"

all_ids = [make_id(doc, i) for i, doc in enumerate(split_docs)]

# Fetch existing IDs from the collection
existing_ids = set(vectorstore._collection.get(include=[])["ids"])
print(f"   -> Existing IDs retrieved: {len(existing_ids)}")

# Filter to only un-indexed docs
pending = [
    (doc, doc_id)
    for doc, doc_id in zip(split_docs, all_ids)
    if doc_id not in existing_ids
]

print(f"   -> Remaining to index: {len(pending)} chunks")

if not pending:
    print("\n[DONE] All chunks already indexed! Nothing to do.")
    print(f"   Collection size: {vectorstore._collection.count()} vectors")
    print("\n[>>] Run: streamlit run app.py")
    sys.exit(0)

# ─────────────────────────────────────────────
#  INDEX PENDING CHUNKS IN BATCHES
# ─────────────────────────────────────────────
total = len(pending)
num_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE
print(f"\n[*] Processing {total} chunks in {num_batches} batches of {BATCH_SIZE}")

for i in range(0, total, BATCH_SIZE):
    batch_pairs = pending[i : i + BATCH_SIZE]
    batch_docs  = [p[0] for p in batch_pairs]
    batch_ids   = [p[1] for p in batch_pairs]
    batch_num   = (i // BATCH_SIZE) + 1

    print(f"\n   [Batch {batch_num}/{num_batches}] Embedding {len(batch_docs)} chunks...")

    retries = 0
    while retries < 6:
        try:
            vectorstore.add_documents(documents=batch_docs, ids=batch_ids)
            print(f"   [Batch {batch_num}/{num_batches}] Done.")
            break
        except Exception as e:
            err_str = str(e)
            if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str:
                wait = BATCH_DELAY + (retries * 30)
                print(f"   [Rate limit] Waiting {wait}s (retry {retries+1}/6)...")
                time.sleep(wait)
                retries += 1
            else:
                print(f"   [ERROR] {e}")
                sys.exit(1)
    else:
        print(f"   [WARN] Could not complete batch {batch_num} after 6 retries.")
        print(f"   [INFO] Progress saved. Re-run this script to continue from where it left off.")
        sys.exit(1)

    if i + BATCH_SIZE < total:
        print(f"   [*] Waiting {BATCH_DELAY}s before next batch...")
        time.sleep(BATCH_DELAY)

# ─────────────────────────────────────────────
#  DONE
# ─────────────────────────────────────────────
final_count = vectorstore._collection.count()
print(f"\n[DONE] ChromaDB complete!")
print(f"   Collection size: {final_count} vectors")
print(f"   Location: {CHROMA_DB_DIR}")
print("\n[>>] Run: streamlit run app.py")