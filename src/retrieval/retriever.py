"""Retrieval helpers with observable relevance scores."""
import logging
from src.config import settings

logger = logging.getLogger('supportpearlz')


def retrieve(store, query: str, k: int | None = None):
    """Return (Document, relevance) pairs; larger relevance values are better."""
    count = k or settings.retrieval_k
    hits = store.similarity_search_with_relevance_scores(query, k=count)
    logger.info(
        'retrieval query=%r hit_count=%d scores=%s sources=%s threshold=%.3f',
        query,
        len(hits),
        [round(float(score), 4) for _, score in hits],
        [doc.metadata.get('source', 'unknown') for doc, _ in hits],
        settings.score_threshold,
    )
    return hits
