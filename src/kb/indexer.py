"""
Knowledge Base Indexer and Pipeline Orchestrator
Builds clean, structured KB records, chunking, and indexes from raw inputs.
Saves processed artifacts to data/processed/.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
from .schema import KBRecord, KBChunk
from .cleaner import (
    PIIRedactor,
    TerminologyStandardizer,
    ContentDeduplicator,
    DocumentExtractor
)


class KBIndexer:
    def __init__(self, raw_data_dir: str = "data/raw", processed_dir: str = "data/processed"):
        self.raw_data_dir = Path(raw_data_dir)
        self.processed_dir = Path(processed_dir)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.deduplicator = ContentDeduplicator(similarity_threshold=0.80)
        self.pii_stats_total = {"ssn": 0, "phone": 0, "email": 0, "credit_card": 0}
        self.duplicates_removed = 0

    def ingest_all(self) -> Tuple[List[KBRecord], List[KBChunk]]:
        raw_sections: List[Dict[str, Any]] = []

        # 1. Parse HTML Web Brochure
        html_file = self.raw_data_dir / "apexcare_plans_web.html"
        if html_file.exists():
            with open(html_file, "r", encoding="utf-8") as f:
                html_sections = DocumentExtractor.parse_html_brochure(f.read(), html_file.name)
                raw_sections.extend(html_sections)

        # 2. Parse Policy Terms & Exclusions
        policy_file = self.raw_data_dir / "policy_terms_exclusions.txt"
        if policy_file.exists():
            with open(policy_file, "r", encoding="utf-8") as f:
                pol_sections = DocumentExtractor.parse_policy_text(f.read(), policy_file.name)
                raw_sections.extend(pol_sections)

        # 3. Parse Underwriting Qualification Rules JSON
        uw_file = self.raw_data_dir / "underwriting_rules.json"
        if uw_file.exists():
            with open(uw_file, "r", encoding="utf-8") as f:
                uw_data = json.load(f)
                uw_sections = DocumentExtractor.parse_underwriting_json(uw_data, uw_file.name)
                raw_sections.extend(uw_sections)

        # 4. Parse FAQ and Objection Guide
        faq_file = self.raw_data_dir / "faq_objection_guide.txt"
        if faq_file.exists():
            with open(faq_file, "r", encoding="utf-8") as f:
                faq_sections = DocumentExtractor.parse_faq_objections(f.read(), faq_file.name)
                raw_sections.extend(faq_sections)

        # 5. Parse Customer Intake Logs (Contains PII to sanitize)
        pii_file = self.raw_data_dir / "customer_intake_forms_pii.txt"
        if pii_file.exists():
            with open(pii_file, "r", encoding="utf-8") as f:
                pii_sections = DocumentExtractor.parse_pii_customer_logs(f.read(), pii_file.name)
                raw_sections.extend(pii_sections)

        # Process, sanitize, standardize, and deduplicate
        records: List[KBRecord] = []
        category_counters: Dict[str, int] = {}

        for item in raw_sections:
            raw_text = item["content"]

            # Step A: PII Identification & Redaction
            sanitized_text, pii_counts = PIIRedactor.redact(raw_text)
            for k, v in pii_counts.items():
                self.pii_stats_total[k] += v

            # Step B: Terminology & Style Standardization
            standardized_text = TerminologyStandardizer.standardize(sanitized_text)

            # Step C: Deduplication Check
            is_dup, reason = self.deduplicator.is_duplicate(standardized_text)
            if is_dup:
                self.duplicates_removed += 1
                continue

            # Step D: Schema Construction with Stable ID
            cat = item["category"]
            category_counters[cat] = category_counters.get(cat, 0) + 1
            rec_id = f"kb_{cat}_{category_counters[cat]:03d}"

            record = KBRecord(
                record_id=rec_id,
                title=item["title"],
                content=standardized_text,
                category=cat,
                source=item["source"],
                version="1.0",
                pii_sanitized=True,
                effective_date="2026-01-01",
                metadata=item.get("metadata", {})
            )
            records.append(record)

        # Step E: Semantic Chunking
        chunks: List[KBChunk] = []
        for rec in records:
            rec_chunks = self._chunk_record(rec)
            chunks.extend(rec_chunks)

        # Save Processed Records and Chunks
        self._save_artifacts(records, chunks)
        return records, chunks

    def _chunk_record(self, record: KBRecord, max_chunk_chars: int = 600, overlap_chars: int = 100) -> List[KBChunk]:
        """
        Chunks long records into coherent passages while retaining metadata.
        """
        text = record.content
        if len(text) <= max_chunk_chars:
            return [KBChunk(
                chunk_id=f"{record.record_id}_c0",
                record_id=record.record_id,
                title=record.title,
                chunk_text=text,
                category=record.category,
                source=record.source,
                metadata=record.metadata
            )]

        # Split on paragraph or double newline
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = []
        current_len = 0
        chunk_idx = 0

        for p in paragraphs:
            p_len = len(p)
            if current_len + p_len > max_chunk_chars and current_chunk:
                chunk_content = "\n\n".join(current_chunk).strip()
                chunks.append(KBChunk(
                    chunk_id=f"{record.record_id}_c{chunk_idx}",
                    record_id=record.record_id,
                    title=record.title,
                    chunk_text=chunk_content,
                    category=record.category,
                    source=record.source,
                    metadata=record.metadata
                ))
                chunk_idx += 1
                # Retain overlap if feasible
                current_chunk = [p]
                current_len = p_len
            else:
                current_chunk.append(p)
                current_len += p_len + 2

        if current_chunk:
            chunks.append(KBChunk(
                chunk_id=f"{record.record_id}_c{chunk_idx}",
                record_id=record.record_id,
                title=record.title,
                chunk_text="\n\n".join(current_chunk).strip(),
                category=record.category,
                source=record.source,
                metadata=record.metadata
            ))

        return chunks

    def _save_artifacts(self, records: List[KBRecord], chunks: List[KBChunk]):
        records_path = self.processed_dir / "kb_records.json"
        chunks_path = self.processed_dir / "kb_chunks.json"
        stats_path = self.processed_dir / "pipeline_stats.json"

        with open(records_path, "w", encoding="utf-8") as f:
            json.dump([r.model_dump() for r in records], f, indent=2)

        with open(chunks_path, "w", encoding="utf-8") as f:
            json.dump([c.model_dump() for c in chunks], f, indent=2)

        stats = {
            "total_records_indexed": len(records),
            "total_chunks_created": len(chunks),
            "duplicates_filtered": self.duplicates_removed,
            "pii_redacted_counts": self.pii_stats_total,
            "categories": {cat: sum(1 for r in records if r.category == cat) for cat in ["product", "policy", "qualification", "faq", "objection"]}
        }

        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)


if __name__ == "__main__":
    indexer = KBIndexer()
    records, chunks = indexer.ingest_all()
    print(f"Indexed {len(records)} KB records and {len(chunks)} chunks.")
