"""Retrieval-only evaluation baseline. Run after building the index: python -m evaluation.run_eval"""
import json, csv
from pathlib import Path
from src.retrieval.vector_store import load_store
from src.retrieval.retriever import retrieve

def main():
    key=input('OpenAI API key (used for this run only): ').strip()
    store=load_store(key); cases=json.loads(Path('evaluation/test_questions.json').read_text()); results=[]
    for case in cases:
        hits=retrieve(store,case['question']); sources=list(dict.fromkeys(d.metadata.get('source','') for d,_ in hits))
        expected=[x.strip() for x in case['ground_truth_source'].split(';') if x.strip()]
        hit=any(any(exp.lower() in src.lower() for src in sources) for exp in expected) if expected else not bool(hits)
        results.append({'id':case['id'],'category':case['category'],'question':case['question'],'retrieved_sources':sources,'retrieval_hit':hit,'expected_sources':expected,'verdict':'retrieval_hit' if hit else 'miss'})
    out=Path('evaluation/results'); out.mkdir(parents=True,exist_ok=True)
    (out/'evaluation_results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    with (out/'evaluation_results.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=results[0].keys()); writer.writeheader(); writer.writerows(results)
    summary={'cases':len(results),'retrieval_hit_rate':sum(x['retrieval_hit'] for x in results)/len(results),'note':'This is retrieval-only, not an LLM groundedness or citation-accuracy score. Review results manually and record failure attribution.'}
    (out/'evaluation_summary.json').write_text(json.dumps(summary,indent=2)); print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
