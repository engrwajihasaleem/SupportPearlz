"""Grounded RAG chain with query condensation, relevance gate and validated citations."""
import logging
import re
import time
from langchain_openai import ChatOpenAI
from src.config import settings
from src.chains.schemas import SupportAnswer
from src.chains.prompts import RAG_PROMPT
from src.chains.memory import condense_question
from src.retrieval.retriever import retrieve

logger = logging.getLogger('supportpearlz')


def answer_question(question: str, history: list, store, api_key: str) -> tuple[SupportAnswer, str, list]:
    started = time.perf_counter()
    try:
        llm = ChatOpenAI(model=settings.llm_model, temperature=settings.temperature, api_key=api_key, timeout=45, max_retries=1)
        standalone = condense_question(question, history, llm) if history else question
        if not standalone:
            standalone = question
        hits = retrieve(store, standalone)
        logger.info('query=%r rewritten=%r', question, standalone)

        if not hits or max(float(score) for _, score in hits) < settings.score_threshold:
            result = SupportAnswer(
                answer='I could not find supporting information for that question in the Pearlz documentation. Please contact human support at support@pearlzhome.example.',
                sources=[], confidence='none', answered=False,
            )
            logger.info('refusal=true reason=below_relevance_threshold latency=%.3f', time.perf_counter() - started)
            return result, standalone, []

        blocks = []
        mapping = {}
        for i, (doc, score) in enumerate(hits[:settings.retrieval_k], start=1):
            label = f'S{i}'
            mapping[label] = doc
            loc = doc.metadata.get('location', 'location not recorded')
            blocks.append(f'[{label}] source={doc.metadata.get("source")} location={loc} relevance={float(score):.3f}\n{doc.page_content[:2200]}')
        context = '\n\n---\n\n'.join(blocks)[:12000]
        chain = RAG_PROMPT | llm.with_structured_output(SupportAnswer)
        result = chain.invoke({'history': '(no prior turns)' if not history else str(history[-8:]), 'context': context, 'question': standalone})

        # Some provider/model combinations populate the answer's [S#] markers but omit
        # the structured sources array. Recover only labels that were actually supplied.
        claimed = list(result.sources or [])
        claimed.extend(re.findall(r'\[(S\d+)\]', result.answer or ''))
        valid = []
        for label in claimed:
            if label in mapping and label not in valid:
                valid.append(label)
        result.sources = valid

        if not result.answered or result.confidence == 'none':
            result.answered = False
            result.confidence = 'none'
            result.sources = []
            result.answer = result.answer or 'I could not find supporting information in the Pearlz documentation. Please contact human support.'
            logger.info('refusal=true latency=%.3f', time.perf_counter() - started)
            return result, standalone, []

        if not valid:
            result.answered = False
            result.confidence = 'none'
            result.answer = 'I could not verify a supporting source for that answer. Please contact human support.'
            logger.warning('answer converted to refusal: model returned no verifiable citation labels')
            return result, standalone, []

        logger.info('retrieved=%s citations=%s refusal=false latency=%.3f', [d.metadata.get('source') for d, _ in hits], valid, time.perf_counter() - started)
        return result, standalone, [(label, mapping[label]) for label in valid]
    except Exception:
        logger.exception('RAG request failed')
        raise
