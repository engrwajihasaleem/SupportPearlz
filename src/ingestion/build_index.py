"""Build persistent Chroma index: python -m src.ingestion.build_index [--rebuild]."""
import argparse, json, time
from pathlib import Path
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from src.config import settings, BASE_DIR
from src.ingestion.loaders import load_directory
from src.ingestion.chunking import split_documents
from src.utils.logging_setup import configure_logging

def build_index(api_key:str|None=None,rebuild:bool=False):
    logger=configure_logging(); docs,report=load_directory(str(BASE_DIR / 'data' / 'knowledge_base'))
    if not docs: raise RuntimeError('No supported, non-empty knowledge-base documents found.')
    chunks=split_documents(docs); (BASE_DIR / 'evaluation' / 'results').mkdir(parents=True,exist_ok=True)
    (BASE_DIR / 'evaluation' / 'results' / 'ingestion_report.json').write_text(json.dumps({**report,'chunk_count':len(chunks)},indent=2),encoding='utf-8')
    embeddings=OpenAIEmbeddings(model=settings.embedding_model,api_key=api_key)
    path=settings.vector_store_path
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    if (Path(path) / 'chroma.sqlite3').exists() and not rebuild:
        try:
            store=Chroma(persist_directory=path,embedding_function=embeddings,collection_name='pearlz_kb')
            if store._collection.count() > 0:
                logger.info('Loaded existing persistent index (%s chunks); no re-embedding performed.', store._collection.count())
                return store,report,0
        except Exception:
            logger.warning('Existing index is unreadable or incompatible; rebuilding it.')
        rebuild=True
    if rebuild and Path(path).exists():
        import shutil; shutil.rmtree(path)
    store=Chroma.from_documents(chunks,embeddings,persist_directory=path,collection_name='pearlz_kb')
    logger.info('Index built: %s source docs, %s chunks',len(docs),len(chunks))
    return store,report,len(chunks)
def main():
    p=argparse.ArgumentParser(); p.add_argument('--rebuild',action='store_true'); p.add_argument('--api-key',default=None,help='Avoid shell history; prefer runtime UI key.'); a=p.parse_args()
    build_index(a.api_key,a.rebuild)
if __name__=='__main__': main()
