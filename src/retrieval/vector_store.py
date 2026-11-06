"""Persistent Chroma vector-store access with clear readiness checks."""
from pathlib import Path
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from src.config import settings


def index_path() -> Path:
    return Path(settings.vector_store_path)


def index_status() -> dict:
    """Report whether the persistent Chroma collection exists and has vectors."""
    path = index_path()
    db_file = path / "chroma.sqlite3"
    if not db_file.exists():
        return {"ready": False, "count": 0, "message": "The knowledge index has not been built yet."}
    try:
        # Open without embeddings: this is a local metadata/readiness check.
        store = Chroma(persist_directory=str(path), collection_name="pearlz_kb")
        count = store._collection.count()
        if count <= 0:
            return {"ready": False, "count": 0, "message": "The Chroma database exists, but its Pearlz collection is empty. Rebuild the index."}
        return {"ready": True, "count": count, "message": f"Knowledge index ready ({count} indexed chunks)."}
    except Exception as exc:
        return {"ready": False, "count": 0, "message": "The saved knowledge index could not be opened. An administrator should rebuild it."}


def get_embeddings(api_key: str):
    return OpenAIEmbeddings(model=settings.embedding_model, api_key=api_key)


def load_store(api_key: str):
    status = index_status()
    if not status["ready"]:
        raise FileNotFoundError(status["message"] + " Sign in as an administrator, open Admin Console → Knowledge Base, and select Build knowledge index.")
    return Chroma(persist_directory=str(index_path()), embedding_function=get_embeddings(api_key), collection_name="pearlz_kb")
