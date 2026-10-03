"""
Mock CRM and Lead Quotation Engine (Question 1 Business Action)
Stores generated leads, eligibility verdicts, and calculates quotes.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel, Field


class LeadQuotation(BaseModel):
    lead_id: str
    caller_name: str
    age: Optional[int] = None
    pre_existing_conditions: List[str] = Field(default_factory=list)
    plan_tier: str = "Silver"
    estimated_monthly_premium: float = 320.0
    qualification_status: str = "QUALIFIED"  # "QUALIFIED", "INELIGIBLE", "ESCALATED_UNDERWRITING"
    notes: str = ""
    citations_used: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class MockCRM:
    def __init__(self, storage_path: str = "data/processed/mock_crm_leads.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.leads: Dict[str, LeadQuotation] = {}
        self._load()

    def _load(self):
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        lead = LeadQuotation(**item)
                        self.leads[lead.lead_id] = lead
            except Exception:
                self.leads = {}

    def _save(self):
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump([l.model_dump() for l in self.leads.values()], f, indent=2)

    def calculate_quote(self, age: Optional[int], tier: str, has_pec: bool = False, is_smoker: bool = False) -> Tuple[float, str]:
        # Base pricing
        base_rates = {
            "Bronze": 180.0,
            "Silver": 320.0,
            "Gold": 480.0
        }
        tier = tier.capitalize() if tier else "Silver"
        rate = base_rates.get(tier, 320.0)

        # Age adjustments
        status = "QUALIFIED"
        if age:
            if age > 65:
                status = "INELIGIBLE_OVER_AGE"
            elif age > 50:
                rate *= 1.35
            elif age > 35:
                rate *= 1.15

        if is_smoker:
            rate *= 1.25  # 25% smoker loading per UW_RULE_SMOKER_02

        if has_pec:
            rate *= 1.10  # 10% PEC loading per UW_RULE_PEC_03

        return round(rate, 2), status

    def create_lead(
        self,
        caller_name: str,
        age: Optional[int],
        pre_existing_conditions: List[str],
        plan_tier: str = "Silver",
        notes: str = "",
        citations_used: List[str] = None
    ) -> LeadQuotation:
        lead_count = len(self.leads) + 1
        lead_id = f"LEAD-2026-{lead_count:04d}"

        has_pec = len(pre_existing_conditions) > 0 and pre_existing_conditions[0].lower() not in ["none", "no", "clean"]
        premium, status = self.calculate_quote(age, plan_tier, has_pec=has_pec)

        if age and age > 65:
            status = "ESCALATED_UNDERWRITING"

        quotation = LeadQuotation(
            lead_id=lead_id,
            caller_name=caller_name or "Anonymous Applicant",
            age=age,
            pre_existing_conditions=pre_existing_conditions,
            plan_tier=plan_tier.capitalize() if plan_tier else "Silver",
            estimated_monthly_premium=premium,
            qualification_status=status,
            notes=notes,
            citations_used=citations_used or []
        )

        self.leads[lead_id] = quotation
        self._save()
        return quotation

    def get_all_leads(self) -> List[LeadQuotation]:
        return list(self.leads.values())

