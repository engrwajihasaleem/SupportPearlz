"""Heterogeneous knowledge-base loaders with provenance metadata."""
from pathlib import Path
import csv, hashlib
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
SUPPORTED={'.pdf','.docx','.md','.txt','.csv'}
def load_file(path: Path) -> list[Document]:
    ext=path.suffix.lower(); docs=[]
    if ext=='.pdf': docs=PyPDFLoader(str(path)).load()
    elif ext=='.docx': docs=Docx2txtLoader(str(path)).load()
    elif ext in {'.md','.txt'}: docs=TextLoader(str(path),encoding='utf-8').load()
    elif ext=='.csv':
        with path.open(encoding='utf-8-sig',newline='') as f:
            for i,row in enumerate(csv.DictReader(f),start=2):
                text=' | '.join(f'{k}: {v}' for k,v in row.items() if v not in (None,''))
                if text: docs.append(Document(page_content=text,metadata={'row':i}))
    else: return []
    for d in docs:
        d.page_content=' '.join(d.page_content.split())
        d.metadata.update({'source':path.name,'doc_type':_doc_type(path.name),'version':'1.0','last_updated':'2026-11-06','product_line':'AquaPearl / AeroPearl'})
        if 'page' in d.metadata: d.metadata['location']=f"page {int(d.metadata['page'])+1}"
        elif 'row' in d.metadata: d.metadata['location']=f"row {d.metadata['row']}"
        else:
            heading=next((line.strip('# ').strip() for line in path.read_text(encoding='utf-8',errors='ignore').splitlines() if line.startswith('#')),path.stem)
            d.metadata['location']=heading
        d.metadata['content_hash']=hashlib.sha256(d.page_content.encode()).hexdigest()
    return [d for d in docs if d.page_content]
def _doc_type(name:str)->str:
    n=name.lower()
    if 'manual' in n: return 'manual'
    if 'price' in n: return 'pricing'
    if 'faq' in n: return 'faq'
    if 'guide' in n or 'troubleshooting' in n or 'installation' in n: return 'guide'
    if 'agreement' in n or 'handbook' in n: return 'service'
    return 'policy'
def load_directory(folder:str='data/knowledge_base') -> tuple[list[Document],dict]:
    base=Path(folder); docs=[]; report={'files_found':0,'loaded':0,'skipped':[],'documents':[]}; seen=set()
    for p in sorted(base.rglob('*')):
        if not p.is_file() or p.suffix.lower() not in SUPPORTED: continue
        report['files_found']+=1
        try:
            loaded=load_file(p); unique=[]
            for d in loaded:
                h=d.metadata['content_hash']
                if h not in seen: seen.add(h); unique.append(d)
            if unique:
                docs.extend(unique); report['loaded']+=1
                report['documents'].append({'file':p.name,'type':p.suffix.lower(),'characters':sum(len(x.page_content) for x in unique),'chunks_before_split':len(unique),'metadata':['source','doc_type','version','product_line','location']})
            else: report['skipped'].append({'file':p.name,'reason':'empty or duplicate content'})
        except Exception as exc: report['skipped'].append({'file':p.name,'reason':str(exc)})
    return docs,report
