# SupportPearlz — Technical Report (working draft)

## 1. Problem and objective
Pearlz Home Systems receives repetitive customer questions whose answers are distributed across product, warranty, return, shipping, service and privacy documents. SupportPearlz is a retrieval-augmented support assistant designed to reduce document-search time while preferring a safe refusal over an unsupported answer.

## 2. Architecture and engineering decisions
The application separates offline ingestion from online querying. The ingestion pipeline dispatches by extension, preserves source metadata, removes duplicate content, applies a recursive character splitter, embeds chunks using `text-embedding-3-small`, and persists them in Chroma. The query pipeline rewrites follow-ups, retrieves semantically relevant chunks, applies a configurable relevance gate, and composes a LangChain prompt with `gpt-4o-mini`. The response is validated with a Pydantic schema and source labels are checked against the supplied context labels.

## 3. Chunking experiment plan
Run the six required configurations on the same authored corpus and five labelled sample questions. Record chunk count, mean/max chunk length and answer-containing top-4 hits. Suggested matrix: 300/0, 300/60, 800/0, 800/120, 1500/0 and 1500/225 characters. The current runtime baseline is 800 characters with 120 overlap. These are starting settings, not claimed experimental winners. Insert measured results after running the experiment.

| Size | Overlap | Chunk count | Mean length | Max length | Answer found in top 4 |
|---:|---:|---:|---:|---:|---:|
| 300 | 0 | To measure | To measure | To measure | To measure |
| 300 | 60 | To measure | To measure | To measure | To measure |
| 800 | 0 | To measure | To measure | To measure | To measure |
| 800 | 120 | To measure | To measure | To measure | To measure |
| 1500 | 0 | To measure | To measure | To measure | To measure |
| 1500 | 225 | To measure | To measure | To measure | To measure |

Smaller chunks can improve topical precision but may remove qualifiers and surrounding context. Larger chunks preserve context but may dilute similarity ranking. Choose the final setting from measured top-4 retrieval performance, not from a tutorial default.

## 4. Embeddings and vector store
The embedding model is configured as `text-embedding-3-small` for both indexing and queries. The same model must be used on both sides because vector dimensions and semantic spaces are model-specific. Chroma persists vectors and metadata to `data/vector_store/`, so query startup does not need to re-embed the corpus. For a policy update, a production implementation should delete chunks by source and upsert the revised document; the current admin rebuild path supports a clean full rebuild.

## 5. Retrieval comparison
Run and record similarity k=3, similarity k=8 and MMR on the same labelled question set. Use hit@k as the retrieval metric. Calibrate `SCORE_THRESHOLD` against actual score distributions; the default is a provisional setting and must be validated empirically.

## 6. Prompt evolution and safety
The final prompt specifies source-only grounding, refusal, partial answers, citation labels, concise tone and prompt-injection resistance. A weak prompt comparison must be performed during evaluation and documented with actual model outputs. Retrieved text and user instructions are treated as data, not as privileged instructions.

## 7. Evaluation and limitations
The supplied 20-case set includes factual, multi-document, follow-up, unanswerable, ambiguous, adversarial and robustness categories. `python -m evaluation.run_eval` measures retrieval-source hits only. It does not claim answer correctness, groundedness, refusal accuracy or citation precision. Execute the full live evaluation, save outputs, manually inspect misses, and attribute failures to loading, chunking, retrieval, rewriting, prompting or generation. Do not report 100% success without evidence.

## 8. Security and deployment
Passwords are stored as salted PBKDF2 hashes. Admin provisioning is environment-controlled and regular registration cannot assign admin role. The OpenAI key is validated at runtime and kept in Streamlit session state; it is not written to project files or database. Docker volumes preserve the database and index. This prototype still requires production security review, HTTPS, rate limiting, CSRF/session hardening, account recovery, audit controls and data-protection review before real customer use.

## 9. Next steps
Capture six real screenshots, execute all evaluation cases, add measured chunking/retrieval comparisons, export a final 4–8-page PDF report, and record the requested 5–8-minute demonstration. Explain the code and trade-offs during the viva.
