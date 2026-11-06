"""Validated configuration for SupportPearlz."""
from dataclasses import dataclass
import os
from dotenv import load_dotenv
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")
@dataclass(frozen=True)
class Settings:
    llm_model: str = os.getenv('LLM_MODEL','gpt-4o-mini')
    embedding_model: str = os.getenv('EMBEDDING_MODEL','text-embedding-3-small')
    temperature: float = float(os.getenv('TEMPERATURE','0'))
    chunk_size: int = int(os.getenv('CHUNK_SIZE','800'))
    chunk_overlap: int = int(os.getenv('CHUNK_OVERLAP','120'))
    retrieval_k: int = int(os.getenv('RETRIEVAL_K','6'))
    score_threshold: float = float(os.getenv('SCORE_THRESHOLD','0.08'))
    vector_store_path: str = os.getenv('VECTOR_STORE_PATH',str(BASE_DIR / 'data' / 'vector_store'))
    log_level: str = os.getenv('LOG_LEVEL','INFO')
settings=Settings()
def masked_config() -> dict:
    return {'llm_model':settings.llm_model,'embedding_model':settings.embedding_model,'temperature':settings.temperature,'chunk_size':settings.chunk_size,'chunk_overlap':settings.chunk_overlap,'retrieval_k':settings.retrieval_k,'score_threshold':settings.score_threshold,'vector_store_path':settings.vector_store_path,'api_key':'provided at runtime; never persisted'}
if __name__=='__main__':
    print(masked_config())
