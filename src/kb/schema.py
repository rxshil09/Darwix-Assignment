"""
Pydantic Schemas for Knowledge Base Records, Chunks, and Retrieval Provenance
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class KBRecord(BaseModel):
    """
    Standardized Knowledge Base Record Schema.
    Designed according to Question 2 requirements:
    record_id, title, content, category, source, version, pii_sanitized, metadata.
    """
    record_id: str = Field(..., description="Unique record identifier e.g. kb_product_001")
    title: str = Field(..., description="Human-readable title or topic")
    content: str = Field(..., description="Cleaned, normalized text content")
    category: str = Field(..., description="Taxonomy category: product | policy | qualification | faq | objection")
    source: str = Field(..., description="Source provenance (e.g. apexcare_plans_web.html, policy_terms_exclusions.txt#Sec1)")
    version: str = Field(default="1.0", description="Record versioning")
    pii_sanitized: bool = Field(default=True, description="Flag indicating PII scrub status")
    effective_date: str = Field(default="2026-01-01", description="Effective policy date")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom metadata tags, plan_tier, age limits")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class KBChunk(BaseModel):
    """
    Fine-grained semantic chunk derived from a KBRecord for vector/BM25 retrieval.
    """
    chunk_id: str = Field(..., description="Unique chunk id e.g. kb_product_001_c0")
    record_id: str = Field(..., description="Parent KBRecord ID")
    title: str
    chunk_text: str
    category: str
    source: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RetrievalCitation(BaseModel):
    """
    Citation model guaranteeing provenance for voice agent and RAG responses.
    """
    record_id: str
    title: str
    source: str
    category: str
    score: float
    snippet: str


class SearchResult(BaseModel):
    """
    Top-k search result package returned to the Voice Agent tool.
    """
    query: str
    total_found: int
    top_score: float
    citations: List[RetrievalCitation]
    context_text: str
    confidence_verdict: str  # "HIGH", "MEDIUM", "LOW", "NO_MATCH"
