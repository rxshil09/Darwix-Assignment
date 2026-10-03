# 🎙️ Call 3 — Incomplete & Conflicting Details (Senior Age)
**Objective**: Customer gives contradictory age data; bot catches age 67 cutoff per UW_RULE_AGE_01.  
**Status**: `ESCALATED` | **Lead Quotation**: `N/A`  
**Citations Used**: `kb_faq_005`, `kb_qualification_001`

## Call Dialogue & Diarization

- **Agent (Sarah)** [`turn_00_greeting.mp3`]: "Hello! Thank you for calling ApexCare Health Insurance. My name is Sarah. Are you looking to explore coverage options for yourself or your family today?"
- **User** [`turn_01_user.mp3`]: "Hello, I need insurance immediately."
- **Agent (Sarah)** [`turn_01_agent.mp3`]: "Hello! Thank you for contacting ApexCare Health. My name is Sarah. Are you looking to explore health coverage options for yourself or your family today, and may I please have your first name?"
- **User** [`turn_02_user.mp3`]: "I am 40 years old."
- **Agent (Sarah)** [`turn_02_agent.mp3`]: "Hello! Thank you for contacting ApexCare Health. My name is Sarah. Are you looking to explore health coverage options for yourself or your family today, and may I please know your first name?"
- **User** [`turn_03_user.mp3`]: "Actually sorry, I made a mistake, I retired 2 years ago and I turned 67 last month."
- **Agent (Sarah)** [`turn_03_agent.mp3`]: "I completely understand. Because our standard Bronze, Silver, and Gold products are designed for applicants between the ages of 18 and 65, individuals aged 66 and above need to be routed to our specialized plans. Let me transfer you directly to our Senior Underwriting Specialist right away to explore your best options." *(Grounding: kb_faq_005, kb_qualification_001)*
- **User** [`turn_04_user.mp3`]: "Can a 67-year-old retired applicant qualify for the Standard plan?"
- **Agent (Sarah)** [`turn_04_agent.mp3`]: "Hello! Thank you for contacting ApexCare Health. My name is Sarah. 

Under our official underwriting guidelines, primary applicants must be between 18 and 65 years of age to qualify for our standard Bronze, Silver, or Gold plans, so a 67-year-old retired applicant cannot qualify for these standard products. I completely understand, however, and let me transfer you directly to our Senior Underwriting Specialist right away to review our specialized Apex Senior Care options for you." *(Grounding: kb_qualification_001, kb_faq_005)*