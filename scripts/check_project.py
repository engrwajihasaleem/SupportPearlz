from pathlib import Path
required=['app.py','requirements.txt','Dockerfile','docker-compose.yml','src/config.py','src/chains/rag_chain.py','evaluation/test_questions.json']
missing=[x for x in required if not Path(x).exists()]
print('Missing:',missing if missing else 'none')
print('Knowledge base files:',len(list(Path('data/knowledge_base').glob('*'))))
print('Evaluation cases:',len(__import__('json').loads(Path('evaluation/test_questions.json').read_text())))
raise SystemExit(1 if missing else 0)
