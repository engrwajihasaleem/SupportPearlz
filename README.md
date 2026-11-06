# SupportPearlz — LangChain RAG Customer Support Agent

A working assignment prototype for fictional Pearlz Home Systems. It includes user registration/login, a restricted admin console, runtime-only OpenAI key validation, multi-format document ingestion, persistent Chroma vector search, LangChain grounded generation, query rewriting, citations, refusal behaviour, logging, an evaluation harness, and Docker deployment.

> **Important:** This is an academic prototype, not a production customer-support system. Review answers before acting on them. All company policies and contact details are fictional.

## 1. Requirements
- Python 3.11 or 3.12 recommended (assignment minimum Python 3.10+).
- Docker Desktop for container deployment.
- An OpenAI API key with access to the configured chat and embedding models.
- Internet access for initial package installation and model API calls. Source documents and the Chroma index are stored locally.

## 2. Local setup (Windows PowerShell)
```powershell
cd SupportPearlz
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```
Do not place an API key in `.env`. The key is entered into the app's validation screen and held only in Streamlit session state.

## 3. Start the app
```powershell
streamlit run app.py
```
First create the administrator account securely in the same PowerShell session (before starting Streamlit):
```powershell
$env:ADMIN_EMAIL="your-admin-email@example.com"
$env:ADMIN_PASSWORD="Choose-A-Long-Unique-Password"
streamlit run app.py
```
If you omit these variables, the app does not create a default administrator. The first admin must be provisioned with the environment variables above. Registration creates standard user accounts only; there is no public admin registration.

## 4. Build the knowledge index
Sign in as admin, open **Admin Console → Knowledge Base**, and select **Build knowledge index**. The app reads `data/knowledge_base/`, loads Markdown and CSV (and supports PDF, DOCX and TXT), chunks with a recursive character splitter, embeds with the configured embedding model, and persists the Chroma collection under `data/vector_store/`.

CLI alternative (provide the key interactively via environment only for this process):
```powershell
$env:OPENAI_API_KEY="your-key"
python -m src.ingestion.build_index --rebuild
```
Do not commit shell history, `.env`, credentials, user database or vector index.

## 5. Test
```powershell
python -m src.config
python -m pytest
python -m evaluation.run_eval
```
The evaluation script reports retrieval hit rate against the authored expected source labels. It is a retrieval-only baseline, not a claim of 100% answer accuracy, groundedness or citation precision. Review each miss and record failure attribution in your report.

## 6. Docker local test
Build from the project root:
```powershell
docker build -t supportpearlz:1.0 .
docker run --name supportpearlz -p 8501:8501 -e ADMIN_EMAIL="admin@example.com" -e ADMIN_PASSWORD="Choose-A-Long-Unique-Password" -v supportpearlz_data:/app/data -v supportpearlz_logs:/app/logs supportpearlz:1.0
```
Open `http://localhost:8501`. Enter your OpenAI key in the app. Build the index from Admin Console. Stop/remove:
```powershell
docker stop supportpearlz
docker rm supportpearlz
```
The named volume preserves the user database and vector index. To inspect logs: `docker logs -f supportpearlz`.

## 7. Docker Hub publishing
1. Create a public repository named `supportpearlz` on Docker Hub.
2. Sign in: `docker login`.
3. Tag: `docker tag supportpearlz:1.0 YOUR_DOCKERHUB_USERNAME/supportpearlz:1.0`.
4. Push: `docker push YOUR_DOCKERHUB_USERNAME/supportpearlz:1.0`.
5. Test pull on another machine: `docker pull YOUR_DOCKERHUB_USERNAME/supportpearlz:1.0` then run the same `docker run` command with the published image name.

Do not include your API key in Docker build arguments, image layers, Compose files, screenshots or Git history.

## 8. GitHub upload
Create an empty GitHub repository named `SupportPearlz`, then from this folder:
```powershell
git init
git add .
git status
git commit -m "Initial SupportPearlz RAG application"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/SupportPearlz.git
git push -u origin main
```
Before committing, confirm `.env`, `data/vector_store/`, `data/supportpearlz_users.db`, `logs/` and virtual environments are not staged. Never force-push over work you need to keep.

## 9. Architecture
- **Ingestion path:** knowledge-base files → format-specific loaders → metadata normalization/deduplication → recursive chunking → OpenAI embeddings → persistent Chroma.
- **Query path:** user question + bounded history → query condensation → Chroma similarity retrieval/relevance gate → LangChain prompt + ChatOpenAI structured output → validated answer + source labels → UI.

See `docs/architecture.mmd` and `docs/technical_report.md`.

## 10. Assignment evidence still to capture
The `docs/screenshots/` folder is intentionally empty. Capture real screenshots on your machine for ingestion, index build, cited answer, refusal, follow-up rewrite, and graceful error handling. Run the evaluation and update the report with actual measured outputs. Do not present placeholder or unexecuted measurements as results.

## Configuration
All tunables are read in `src/config.py` from environment variables: `LLM_MODEL`, `EMBEDDING_MODEL`, `TEMPERATURE`, `CHUNK_SIZE`, `CHUNK_OVERLAP`, `RETRIEVAL_K`, `SCORE_THRESHOLD`, `VECTOR_STORE_PATH`, `LOG_LEVEL`. Admin provisioning uses `ADMIN_EMAIL` and `ADMIN_PASSWORD`. The API key is provided at runtime and never persisted by the application.

## Troubleshooting: API key and knowledge index

- **Invalid API key:** the login gate now explains that the key was rejected and asks you to check that it is active and copied correctly. The rejected value is cleared from the Streamlit session.
- **Quota / billing / permission:** check API billing, project usage limits, and model access in the OpenAI platform. A valid ChatGPT subscription is separate from API billing.
- **Network / timeout / rate limit:** check connectivity, wait and retry, or review API usage limits. The UI shows a short actionable message; detailed diagnostic information is written to the application log.
- **No supporting source found:** first check the green **Knowledge index ready** status at the top of Support Chat. If the index is missing or empty, sign in as the administrator and use **Admin Console → Knowledge Base → Build knowledge index**. The source documents are already included under `data/knowledge_base/`; they must be embedded into Chroma before customer accounts can search them.
- **A customer account cannot build the index:** this is intentional. Only the restricted administrator can access the index-building controls.

### Provision the administrator before starting Streamlit (PowerShell)

```powershell
$env:ADMIN_EMAIL="admin@example.com"
$env:ADMIN_PASSWORD="Use-A-Strong-Unique-Password"
python scripts/create_admin.py
streamlit run app.py
```

After validating your API key, sign in with that administrator email/password. Build the knowledge index once. Then sign out and test using a normal registered customer account. If you have changed the source documents or embedding model, select **Force full rebuild** before building again.

The default relevance threshold is now `0.08` to reduce false refusals from borderline semantic matches. It remains configurable through `SCORE_THRESHOLD`; retrieval logs record the actual scores, source filenames and threshold so the value can be tuned using the assignment evaluation set. This is a prototype setting, not a claim of measured optimality.
