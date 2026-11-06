import os, json, time
from pathlib import Path
import streamlit as st
from src.auth import ensure_admin,register,login,users_summary
from src.config import settings
from src.ingestion.build_index import build_index
from src.retrieval.vector_store import load_store
from src.chains.rag_chain import answer_question
from src.retrieval.vector_store import index_status
from src.utils.errors import friendly_error
BASE_DIR=Path(__file__).resolve().parent
st.set_page_config(page_title='SupportPearlz | Pearlz Home Systems',page_icon='💧',layout='wide')
st.markdown("""<style>
:root{--green:#174a35} .stApp{background:#f6f8f6} [data-testid="stSidebar"]{background:#123c2d}
[data-testid="stSidebar"] *{color:#fff!important} .hero{background:linear-gradient(120deg,#123c2d,#267b58);padding:2rem;border-radius:18px;color:white;margin-bottom:1rem}
.hero h1{color:white;font-size:2.2rem}.small{color:#60736a;font-size:.9rem}
</style>""",unsafe_allow_html=True)
st.session_state.setdefault('history',[]); st.session_state.setdefault('messages',[]); st.session_state.setdefault('api_key',''); st.session_state.setdefault('user',None)
ensure_admin(os.getenv('ADMIN_EMAIL','admin@pearlzhome.example'),os.getenv('ADMIN_PASSWORD',''))
def key_screen():
    st.markdown('<div class="hero"><h1>SupportPearlz</h1><p>Grounded customer support, backed by Pearlz documentation.</p></div>',unsafe_allow_html=True)
    st.subheader('Connect your AI provider')
    st.info('Your API key is checked and held only in this browser session. It is not written to .env, source files, or the database.')
    key=st.text_input('OpenAI API key',type='password',placeholder='sk-...',key='openai_api_key_input')
    if st.button('Validate key and continue',type='primary'):
        if not key.strip():
            st.error('Please enter your OpenAI API key.')
        else:
            try:
                from openai import OpenAI
                client=OpenAI(api_key=key.strip(), timeout=15.0, max_retries=0)
                client.models.list()
                st.session_state.api_key=key.strip()
                st.session_state.key_validated=True
                st.success('API key validated successfully. You can now sign in or create an account.')
                st.rerun()
            except Exception as exc:
                st.session_state.api_key=''
                st.session_state.key_validated=False
                st.error(friendly_error(exc, 'validate the API key'))
                st.caption('For security, the rejected key has not been retained in this session.')

def auth_screen():
    st.markdown('<div class="hero"><h1>Welcome to SupportPearlz</h1><p>Pearlz Home Systems • Customer knowledge assistant</p></div>',unsafe_allow_html=True)
    a,b=st.tabs(['Sign in','Create account'])
    with a:
        with st.form('login'):
            email=st.text_input('Email'); password=st.text_input('Password',type='password'); go=st.form_submit_button('Sign in',type='primary')
        if go:
            u=login(email,password)
            if u: st.session_state.user=u; st.rerun()
            else: st.error('Email or password is incorrect.')
    with b:
        with st.form('register'):
            email2=st.text_input('Email address',key='reg_email'); p1=st.text_input('Password (10+ characters)',type='password',key='reg_pw'); p2=st.text_input('Confirm password',type='password'); create=st.form_submit_button('Create free account')
        if create:
            if p1!=p2: st.error('Passwords do not match.')
            else:
                try: register(email2,p1); st.success('Account created. Sign in now.')
                except Exception as e: st.error(str(e))
def main_app():
    user=st.session_state.user
    with st.sidebar:
        st.markdown('## 💧 SupportPearlz')
        st.caption(f"Signed in: {user['email']}")
        st.caption(f"Access: {user['role'].title()}")
        page=st.radio('Navigation',['Support Chat','About & Help'] + (['Admin Console'] if user['role']=='admin' else []))
        if st.button('Sign out'):
            # Clear authentication, the API key, and the password-style input widget.
            st.session_state.api_key = ''
            st.session_state.key_validated = False
            st.session_state.openai_api_key_input = ''
            st.session_state.user = None
            st.session_state.messages = []
            st.session_state.history = []
            st.rerun()
        if st.button('Disconnect API key'):
            st.session_state.api_key = ''
            st.session_state.key_validated = False
            st.session_state.openai_api_key_input = ''
            st.session_state.user = None
            st.session_state.messages = []
            st.session_state.history = []
            st.rerun()

    if page=='Support Chat':
        st.markdown('<div class="hero"><h1>How can we help?</h1><p>Ask about Pearlz products, delivery, installation, warranty, returns, and maintenance.</p></div>',unsafe_allow_html=True)
        status=index_status()
        if status['ready']:
            st.success(status['message'])
        else:
            st.warning('Knowledge base is not ready. ' + status['message'])
            if user['role']=='admin':
                st.info('Open Admin Console → Knowledge Base and build the index before testing customer questions.')
            else:
                st.info('A Pearlz administrator must build the knowledge index before customers can ask questions. Your account does not have administrator permissions.')
        store=None
        if status['ready']:
            try:
                store=load_store(st.session_state.api_key)
            except Exception as exc:
                st.error(friendly_error(exc, 'open the Pearlz knowledge index'))
        for m in st.session_state.messages:
            with st.chat_message(m['role']):
                st.markdown(m['content'])
                if m.get('sources'):
                    with st.expander('Sources used'):
                        for source in m['sources']: st.caption(source)
        question=st.chat_input('Ask a Pearlz support question...', disabled=(store is None))
        if question:
            st.session_state.messages.append({'role':'user','content':question})
            with st.chat_message('user'): st.markdown(question)
            with st.chat_message('assistant'):
                with st.spinner('Searching Pearlz documentation...'):
                    try:
                        result,rewritten,citations=answer_question(question,st.session_state.history,store,st.session_state.api_key)
                        st.markdown(result.answer)
                        source_labels=[]
                        for label,doc in citations:
                            source_labels.append(f"[{label}] **{doc.metadata.get('source','Unknown source')}** — {doc.metadata.get('location','location unavailable')}")
                        if source_labels:
                            st.markdown('**Sources**\n\n'+'\n\n'.join(source_labels))
                        else:
                            st.caption('No supporting source was retrieved. The answer was safely refused.')
                        st.caption(f"Confidence: {result.confidence} • Rewritten query: {rewritten}")
                        st.session_state.history.append({'question':question,'answer':result.answer})
                        st.session_state.history=st.session_state.history[-6:]
                        st.session_state.messages.append({'role':'assistant','content':result.answer,'sources':source_labels})
                    except Exception as exc:
                        st.error(friendly_error(exc, 'answer this support question'))
                        st.caption('Your question has not been treated as answered. You can retry it after checking the service.')
    elif page=='Admin Console':
        st.title('Administrator Console')
        st.caption('Restricted administrator controls')
        t1,t2,t3=st.tabs(['Knowledge Base','Users','Evaluation'])
        with t1:
            st.write('The source documents are stored in `data/knowledge_base/`. Building the index is a separate step that converts them into searchable vectors.')
            kb=BASE_DIR / 'data' / 'knowledge_base'
            files=sorted(p for p in kb.rglob('*') if p.is_file() and p.suffix.lower() in {'.pdf','.docx','.md','.txt','.csv'})
            st.metric('Supported knowledge-base files',len(files))
            with st.expander('View included documents'):
                for f in files: st.write(f'• {f.relative_to(kb)}')
            status=index_status()
            if status['ready']: st.success(status['message'])
            else: st.warning(status['message'])
            rebuild=st.checkbox('Force full rebuild (re-embed every document)',value=False)
            if st.button('Build knowledge index' if not status['ready'] else 'Build / refresh knowledge index',type='primary'):
                try:
                    with st.spinner('Reading source files, creating chunks, embedding and saving the index...'):
                        _,report,n=build_index(st.session_state.api_key,rebuild=True if rebuild else False)
                    st.success(f"Index build completed: {report['loaded']} source files loaded; {n} chunks created; {len(report['skipped'])} skipped.")
                    st.json(report)
                    st.rerun()
                except Exception as exc:
                    st.error(friendly_error(exc, 'build the knowledge index'))
                    st.caption('Check the application log for the technical details. The existing index has not been reported as ready.')
            report_path=BASE_DIR / 'evaluation' / 'results' / 'ingestion_report.json'
            if report_path.exists():
                st.download_button('Download ingestion report',report_path.read_bytes(),'ingestion_report.json')
        with t2:
            rows=users_summary(); st.metric('Registered accounts',len(rows)); st.dataframe(rows,use_container_width=True)
        with t3:
            st.write('Run the retrieval/evaluation harness from the project root:')
            st.code('python -m evaluation.run_eval')
            p=BASE_DIR / 'evaluation' / 'results' / 'evaluation_summary.json'
            if p.exists(): st.json(json.loads(p.read_text()))
    else:
        st.title('About SupportPearlz')
        st.write('SupportPearlz is a retrieval-augmented support assistant for the fictional Pearlz Home Systems company. Answers are grounded in a persistent local vector index and display source citations.')
        st.warning('Prototype notice: verify every answer before using it in a real customer interaction. Do not enter payment-card or other sensitive personal data.')
        st.subheader('Support channels')
        st.write('Human support: support@pearlzhome.example (fictional assignment contact).')
if not st.session_state.api_key: key_screen()
elif not st.session_state.user: auth_screen()
else: main_app()
