"""
Data Collection, Cleaning, Sanitization (PII), and Normalization Pipeline
Implements Question 2 Requirements:
- HTML/PDF/Text parsing & extraction
- Boilerplate & noise removal
- PII identification and masking
- Exact & near-duplicate detection and removal
- Terminology and heading standardization
"""

import re
import hashlib
from typing import List, Dict, Any, Tuple
from bs4 import BeautifulSoup
from .schema import KBRecord


class PIIRedactor:
    """
    Identifies and sanitizes Personally Identifiable Information (PII).
    Masks SSNs, phone numbers, credit card numbers, and email addresses.
    """
    SSN_PATTERN = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
    PHONE_PATTERN = re.compile(r'(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    CREDIT_CARD_PATTERN = re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b')

    @classmethod
    def redact(cls, text: str) -> Tuple[str, Dict[str, int]]:
        stats = {"ssn": 0, "phone": 0, "email": 0, "credit_card": 0}

        def ssn_repl(match):
            stats["ssn"] += 1
            return "[REDACTED_SSN]"

        def phone_repl(match):
            stats["phone"] += 1
            return "[REDACTED_PHONE]"

        def email_repl(match):
            stats["email"] += 1
            return "[REDACTED_EMAIL]"

        def cc_repl(match):
            stats["credit_card"] += 1
            return "[REDACTED_CREDIT_CARD]"

        sanitized = cls.SSN_PATTERN.sub(ssn_repl, text)
        sanitized = cls.CREDIT_CARD_PATTERN.sub(cc_repl, sanitized)
        sanitized = cls.PHONE_PATTERN.sub(phone_repl, sanitized)
        sanitized = cls.EMAIL_PATTERN.sub(email_repl, sanitized)

        return sanitized, stats


class TerminologyStandardizer:
    """
    Standardizes inconsistent insurance terms, informal colloquialisms, and headings.
    """
    SYNONYM_MAP = {
        r'\bco-?pay(ments?)?\b': 'Co-payment',
        r'\bcost[- ]?share\b': 'Co-payment',
        r'\bpre-?existing conditions?\b': 'Pre-Existing Condition (PEC)',
        r'\bpre-?existing illness(es)?\b': 'Pre-Existing Condition (PEC)',
        r'\bpec\b': 'Pre-Existing Condition (PEC)',
        r'\bcashless hospitalization\b': 'Cashless Inpatient Admission',
        r'\bdoc visit\b': 'Primary Care Consultation',
        r'\ber\b': 'Emergency Room',
        r'\bwaiting period\b': 'Mandatory Waiting Period',
    }

    @classmethod
    def standardize(cls, text: str) -> str:
        standardized = text
        for pattern, replacement in cls.SYNONYM_MAP.items():
            standardized = re.sub(pattern, replacement, standardized, flags=re.IGNORECASE)
        # Clean excessive whitespace
        standardized = re.sub(r'[ \t]+', ' ', standardized)
        standardized = re.sub(r'\n{3,}', '\n\n', standardized)
        return standardized.strip()


class ContentDeduplicator:
    """
    Detects and eliminates exact duplicates (SHA256) and near-duplicates (Jaccard similarity).
    """
    def __init__(self, similarity_threshold: float = 0.60):
        self.similarity_threshold = similarity_threshold
        self.seen_hashes = set()
        self.seen_token_sets = []

    def _tokenize(self, text: str) -> set:
        words = re.findall(r'\b\w{3,}\b', text.lower())
        return set(words)

    def is_duplicate(self, text: str) -> Tuple[bool, str]:
        # Exact match check
        content_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        if content_hash in self.seen_hashes:
            return True, "EXACT_HASH_MATCH"

        # Near-duplicate check via Jaccard similarity
        tokens = self._tokenize(text)
        if not tokens:
            return False, "EMPTY"

        for prior_tokens in self.seen_token_sets:
            intersection = len(tokens & prior_tokens)
            union = len(tokens | prior_tokens)
            min_len = min(len(tokens), len(prior_tokens))
            containment = intersection / min_len if min_len > 0 else 0

            if union > 0 and (intersection / union) >= self.similarity_threshold:
                return True, f"NEAR_DUPLICATE_JACCARD_{(intersection/union):.2f}"
            if containment >= 0.80 and min_len >= 8:
                return True, f"CONTAINED_DUPLICATE_{containment:.2f}"

        # Register novel content
        self.seen_hashes.add(content_hash)
        self.seen_token_sets.append(tokens)
        return False, "UNIQUE"


class DocumentExtractor:
    """
    Extracts, cleans, and standardizes records from HTML, structured text, and JSON.
    """
    @classmethod
    def parse_html_brochure(cls, html_content: str, source_name: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html_content, 'html.parser')

        # 1. Remove navigation, headers, footers, scripts, and promo tickers
        for tag in soup(['header', 'footer', 'nav', 'script', 'style', 'aside']):
            tag.decompose()

        for noise in soup.find_all(class_=re.compile(r'(promo-ticker|header-cta|footer-links|disclaimer)')):
            noise.decompose()

        extracted_sections = []

        # 2. Extract plan comparison matrix
        comp_section = soup.find('section', id='plan-comparison-matrix')
        if comp_section:
            title_tag = comp_section.find(['h2', 'h3'])
            title = title_tag.get_text(strip=True) if title_tag else "ApexCare Plan Tier Comparison"
            body_text = comp_section.get_text(separator="\n", strip=True)
            extracted_sections.append({
                "title": title,
                "content": body_text,
                "category": "product",
                "source": f"{source_name}#tier-comparison-matrix",
                "metadata": {"plan_comparison": True, "tiers": ["bronze", "silver", "gold"]}
            })

        # 3. Extract individual plan tiers
        tier_articles = soup.find_all('article', class_='tier-card')
        for article in tier_articles:
            title_tag = article.find(['h2', 'h3'])
            title = title_tag.get_text(strip=True) if title_tag else "ApexCare Coverage Tier"
            tier = article.get('data-tier', 'general')
            body_text = article.get_text(separator="\n", strip=True)

            extracted_sections.append({
                "title": title,
                "content": body_text,
                "category": "product",
                "source": f"{source_name}#{tier}",
                "metadata": {"plan_tier": tier}
            })

        # 4. Extract Cashless Claim Process
        claim_section = soup.find('section', id='cashless-claim-process')
        if claim_section:
            title_tag = claim_section.find(['h2', 'h3'])
            title = title_tag.get_text(strip=True) if title_tag else "Cashless Claim Process"
            body_text = claim_section.get_text(separator="\n", strip=True)
            extracted_sections.append({
                "title": title,
                "content": body_text,
                "category": "faq",
                "source": f"{source_name}#cashless-claims",
                "metadata": {"topic": "claims", "claim_type": "cashless"}
            })

        # 5. Extract repeated promotional sections to test deduplicator
        repeated_sections = soup.find_all('section', class_='repeated-section')
        for rep in repeated_sections:
            for sub_p in rep.find_all('p'):
                p_text = sub_p.get_text(separator="\n", strip=True)
                if len(p_text) > 30:
                    extracted_sections.append({
                        "title": "Marketing Summary Promotional Copy",
                        "content": p_text,
                        "category": "product",
                        "source": f"{source_name}#marketing-summary",
                        "metadata": {"type": "promotional_summary"}
                    })

        return extracted_sections

    @classmethod
    def parse_policy_text(cls, text_content: str, source_name: str) -> List[Dict[str, Any]]:
        sections = []
        # Split on markdown/section headings
        raw_sections = re.split(r'\n(?=(?:SECTION\s+\d+|1\.\d+|2\.\d+|3\.\d+))', text_content)

        for sec in raw_sections:
            clean_sec = sec.strip()
            if len(clean_sec) < 50:
                continue

            lines = clean_sec.split('\n')
            header_line = lines[0].strip()

            # Determine category
            if "EXCLUSION" in header_line.upper():
                cat = "policy"
            elif "WAITING PERIOD" in header_line.upper() or "PEC" in header_line.upper():
                cat = "policy"
            elif "ROOM RENT" in header_line.upper() or "COPAYS" in header_line.upper():
                cat = "product"
            else:
                cat = "policy"

            sections.append({
                "title": header_line[:80],
                "content": clean_sec,
                "category": cat,
                "source": f"{source_name}#{header_line[:30].replace(' ', '_')}",
                "metadata": {"contract_doc": "POL-APEX-2026-V1.0"}
            })

        return sections

    @classmethod
    def parse_faq_objections(cls, text_content: str, source_name: str) -> List[Dict[str, Any]]:
        items = []
        blocks = re.split(r'\n(?=(?:OBJECTION\s+\d+|FAQ\s+\d+))', text_content)

        for blk in blocks:
            clean_blk = blk.strip()
            if not clean_blk:
                continue

            lines = clean_blk.split('\n')
            title_line = lines[0].strip()

            cat = "objection" if "OBJECTION" in title_line.upper() else "faq"

            items.append({
                "title": title_line,
                "content": clean_blk,
                "category": cat,
                "source": f"{source_name}#{title_line[:25].replace(' ', '_')}",
                "metadata": {"doc": "SALES-OBJ-GUIDE-2026"}
            })

        return items

    @classmethod
    def parse_underwriting_json(cls, data: Dict[str, Any], source_name: str) -> List[Dict[str, Any]]:
        records = []
        rules = data.get("rules", [])
        for rule in rules:
            rule_id = rule.get("rule_id", "UW_RULE")
            topic = rule.get("topic", "Underwriting Standard")
            content_parts = [f"Rule: {topic}"]
            if "criteria" in rule:
                content_parts.append(f"Criteria: {rule['criteria']}")
            if "action_if_exceeded" in rule:
                content_parts.append(f"Action: {rule['action_if_exceeded']}")
            if "premium_impact" in rule:
                content_parts.append(f"Premium Impact: {rule['premium_impact']}")
            if "unacceptable_conditions_direct" in rule:
                content_parts.append(f"Ineligible Conditions for Direct Online Issue: {', '.join(rule['unacceptable_conditions_direct'])}")
            if "action_if_unacceptable" in rule:
                content_parts.append(f"Escalation Requirement: {rule['action_if_unacceptable']}")

            full_text = "\n".join(content_parts)
            records.append({
                "title": f"Underwriting Guideline: {topic}",
                "content": full_text,
                "category": "qualification",
                "source": f"{source_name}#{rule_id}",
                "metadata": {"rule_id": rule_id, "doc": data.get("document_code", "UW-STD")}
            })

        return records

    @classmethod
    def parse_pii_customer_logs(cls, text_content: str, source_name: str) -> List[Dict[str, Any]]:
        records = []
        entries = re.split(r'\n(?=LOG_ENTRY\s+#\d+)', text_content)

        for entry in entries:
            clean_entry = entry.strip()
            if not clean_entry or "LOG_ENTRY" not in clean_entry:
                continue

            lines = clean_entry.split('\n')
            title_line = lines[0].strip()

            records.append({
                "title": f"Customer Inquiry Log ({title_line})",
                "content": clean_entry,
                "category": "faq",
                "source": f"{source_name}#{title_line}",
                "metadata": {"source_type": "customer_intake_form"}
            })

        return records
