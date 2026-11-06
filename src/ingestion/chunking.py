from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config import settings
def split_documents(documents, chunk_size:int|None=None, overlap:int|None=None):
    splitter=RecursiveCharacterTextSplitter(chunk_size=chunk_size or settings.chunk_size,chunk_overlap=overlap if overlap is not None else settings.chunk_overlap,add_start_index=True,separators=['\n## ','\n# ','\n\n','\n','. ',' ',''])
    return splitter.split_documents(documents)
