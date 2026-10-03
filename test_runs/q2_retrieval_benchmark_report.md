# 📊 Question 2 — Knowledge Base Retrieval Benchmark Report

This evaluation verifies the production-ready knowledge base against the five required assessment categories.
Each query validates retrieval accuracy, source traceability, relevance, and verdict.

| # | Category | User Question | Top Record ID | Source Reference | Confidence | Verdict |
|---|----------|---------------|---------------|------------------|------------|---------|
| 1 | `product` | What benefits are included in the Gold Tier compared to Silver? | `kb_product_001` | `apexcare_plans_web.html#tier-comparison-matrix` | **HIGH** | ✅ **Correct** |
| 2 | `policy` | What is the waiting period for pre-existing hypertension or diabetes? | `kb_objection_003` | `faq_objection_guide.txt#OBJECTION_3:_"Will_you_co` | **HIGH** | ✅ **Correct** |
| 3 | `qualification` | Can a 67-year-old retired applicant qualify for the Standard plan? | `kb_qualification_001` | `underwriting_rules.json#UW_RULE_AGE_01` | **HIGH** | ✅ **Correct** |
| 4 | `faq` | How do I file a cashless claim at a network hospital? | `kb_faq_001` | `apexcare_plans_web.html#cashless-claims` | **HIGH** | ✅ **Correct** |
| 5 | `objection` | Why is your monthly premium higher than basic health plans? | `kb_objection_001` | `faq_objection_guide.txt#OBJECTION_1:_"Why_is_your` | **HIGH** | ✅ **Correct** |

---

### Query 1: [PRODUCT] What benefits are included in the Gold Tier compared to Silver?
- **User Question:** *"What benefits are included in the Gold Tier compared to Silver?"*
- **Retrieved Record ID:** `kb_product_001`
- **Source Reference:** `apexcare_plans_web.html#tier-comparison-matrix`
- **Retrieval Score:** `0.0328` (Confidence: `HIGH`)
- **Relevance Explanation:** Matched 3 domain keywords (gold, silver, deductible). Correctly retrieved record from product category.
- **Official Verdict:** **Correct**
- **Retrieved Passage:**
> ApexCare Plan Tier Comparison: Gold vs Silver vs Bronze Benefits
Compare benefits across ApexCare Gold, Silver, and Bronze tiers:
Benefit Feature
Bronze Tier
Silver Tier
Gold Tier
Monthly Starting Premium
$180/month
$320/month
$480/month
Annual Deductible (Ind / Fam)
$4,500 / $9,...

### Query 2: [POLICY] What is the waiting period for pre-existing hypertension or diabetes?
- **User Question:** *"What is the waiting period for pre-existing hypertension or diabetes?"*
- **Retrieved Record ID:** `kb_objection_003`
- **Source Reference:** `faq_objection_guide.txt#OBJECTION_3:_"Will_you_co`
- **Retrieval Score:** `0.0325` (Confidence: `HIGH`)
- **Relevance Explanation:** Matched 3 domain keywords (24, pre-existing, pec). Correctly retrieved record from objection category.
- **Official Verdict:** **Correct**
- **Retrieved Passage:**
> OBJECTION 3: "Will you cover my pre-existing diabetes or high blood pressure?"
Category: objection
Standard Grounded Response:
Yes, ApexCare covers Pre-Existing Condition (Pre-Existing Condition (PEC)) such as controlled Type 2 diabetes and hypertension once the mandatory 24-mont...

### Query 3: [QUALIFICATION] Can a 67-year-old retired applicant qualify for the Standard plan?
- **User Question:** *"Can a 67-year-old retired applicant qualify for the Standard plan?"*
- **Retrieved Record ID:** `kb_qualification_001`
- **Source Reference:** `underwriting_rules.json#UW_RULE_AGE_01`
- **Retrieval Score:** `0.0328` (Confidence: `HIGH`)
- **Relevance Explanation:** Matched 4 domain keywords (18, 65, age, senior). Correctly retrieved record from qualification category.
- **Official Verdict:** **Correct**
- **Retrieved Passage:**
> Rule: Eligible Age Range and Senior Retirement Qualification
Criteria: Primary applicant must be between 18 and 65 years of age at the time of policy inception. Dependent children are covered from 91 days to 25 years (if unmarried students). Senior or retired applicants aged 66 a...

### Query 4: [FAQ] How do I file a cashless claim at a network hospital?
- **User Question:** *"How do I file a cashless claim at a network hospital?"*
- **Retrieved Record ID:** `kb_faq_001`
- **Source Reference:** `apexcare_plans_web.html#cashless-claims`
- **Retrieval Score:** `0.0328` (Confidence: `HIGH`)
- **Relevance Explanation:** Matched 4 domain keywords (cashless, pre-authorization, hospital, 48 hours). Correctly retrieved record from faq category.
- **Official Verdict:** **Correct**
- **Retrieved Passage:**
> How to File a Cashless Claim at a Network Hospital
To access Cashless Inpatient Admission without out-of-pocket payment:
Step 1 - Pre-Authorization:
Present your ApexCare digital member ID card at the hospital's TPA / insurance helpdesk at least 48 hours prior to planned admissio...

### Query 5: [OBJECTION] Why is your monthly premium higher than basic health plans?
- **User Question:** *"Why is your monthly premium higher than basic health plans?"*
- **Retrieved Record ID:** `kb_objection_001`
- **Source Reference:** `faq_objection_guide.txt#OBJECTION_1:_"Why_is_your`
- **Retrieval Score:** `0.0328` (Confidence: `HIGH`)
- **Relevance Explanation:** Matched 2 domain keywords (premium, comprehensive). Correctly retrieved record from objection category.
- **Official Verdict:** **Correct**
- **Retrieved Passage:**
> OBJECTION 1: "Why is your monthly premium higher than basic health plans?"
Category: objection
Standard Grounded Response:
ApexCare's premium reflects comprehensive coverage with significantly lower out-of-pocket exposure when you actually need medical care. Unlike basic catastro...
