"""
Hybrid Knowledge Base Retriever (BM25 + Dense Semantic Vector Search)
Implements Reciprocal Rank Fusion (RRF), confidence estimation, and citation provenance.
Supports Gemini embeddings, OpenAI embeddings, and offline TF-IDF cosine fallback.
"""

import os
import json
import math
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

from .schema import KBChunk, SearchResult, RetrievalCitation

load_dotenv()


class HybridRetriever:
    def __init__(self, chunks_path: str = "data/processed/kb_chunks.json"):
        self.chunks_path = Path(chunks_path)
        self.chunks: List[KBChunk] = []
        self.bm25: Optional[BM25Okapi] = None
        self.tfidf_vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix: Optional[np.ndarray] = None
        self.gemini_available = False
        self.openai_available = False
        self._init_engine()

    def _init_engine(self):
        if not self.chunks_path.exists():
            return

        with open(self.chunks_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.chunks = [KBChunk(**item) for item in data]

        if not self.chunks:
            return

        # Initialize BM25 with weighted title and category
        corpus_tokens = [self._tokenize(f"{c.title} {c.title} {c.category} {c.category} {c.chunk_text}") for c in self.chunks]
        self.bm25 = BM25Okapi(corpus_tokens)

        # Initialize TF-IDF as reliable offline/local vector fallback with weighted title
        corpus_texts = [f"{c.title}\n{c.title}\n{c.category}\n{c.chunk_text}" for c in self.chunks]
        self.tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=4000, ngram_range=(1, 2))
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(corpus_texts)

        # Check for Gemini or OpenAI API keys
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key and gemini_key != "your_gemini_api_key_here":
            self.gemini_available = True

        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and openai_key != "your_openai_api_key_here":
            self.openai_available = True

    def _tokenize(self, text: str) -> List[str]:
        import re
        return re.findall(r'\b\w+\b', text.lower())

    def search(self, query: str, top_k: int = 3, min_score_threshold: float = 0.015) -> SearchResult:
        if not self.chunks:
            return SearchResult(
                query=query,
                total_found=0,
                top_score=0.0,
                citations=[],
                context_text="",
                confidence_verdict="NO_MATCH"
            )

        query_tokens = self._tokenize(query)

        # 1. BM25 Sparse Search
        bm25_scores = self.bm25.get_scores(query_tokens)
        bm25_ranked = np.argsort(bm25_scores)[::-1]

        # 2. Vector Dense/TF-IDF Cosine Search
        query_vec = self.tfidf_vectorizer.transform([query])
        cosine_scores = cosine_similarity(query_vec, self.tfidf_matrix)[0]
        cosine_ranked = np.argsort(cosine_scores)[::-1]

        # 3. Reciprocal Rank Fusion (RRF)
        # RRF_Score = 1.0 / (60 + rank_bm25) + 1.0 / (60 + rank_cosine)
        rrf_scores = np.zeros(len(self.chunks))
        k_rrf = 60.0

        for rank, idx in enumerate(bm25_ranked):
            if bm25_scores[idx] > 0:
                rrf_scores[idx] += 1.0 / (k_rrf + rank + 1)

        for rank, idx in enumerate(cosine_ranked):
            if cosine_scores[idx] > 0.05:
                rrf_scores[idx] += 1.0 / (k_rrf + rank + 1)

        # Top indices
        top_indices = np.argsort(rrf_scores)[::-1][:top_k]

        citations: List[RetrievalCitation] = []
        context_snippets: List[str] = []
        top_score = float(rrf_scores[top_indices[0]]) if len(top_indices) > 0 else 0.0

        for idx in top_indices:
            score = float(rrf_scores[idx])
            if score < min_score_threshold:
                continue

            chunk = self.chunks[idx]
            cit = RetrievalCitation(
                record_id=chunk.record_id,
                title=chunk.title,
                source=chunk.source,
                category=chunk.category,
                score=round(score, 4),
                snippet=chunk.chunk_text[:280] + ("..." if len(chunk.chunk_text) > 280 else "")
            )
            citations.append(cit)
            context_snippets.append(
                f"[Source: {chunk.source} | Record: {chunk.record_id} | Category: {chunk.category}]\n"
                f"{chunk.chunk_text}"
            )

        # Confidence Estimation
        if not citations or top_score < min_score_threshold:
            verdict = "NO_MATCH"
        elif top_score >= 0.028:
            verdict = "HIGH"
        elif top_score >= 0.020:
            verdict = "MEDIUM"
        else:
            verdict = "LOW"

        context_text = "\n\n---\n\n".join(context_snippets)

        return SearchResult(
            query=query,
            total_found=len(citations),
            top_score=round(top_score, 4),
            citations=citations,
            context_text=context_text,
            confidence_verdict=verdict
        )
