# 🎙️ Call 1 — Cooperative Customer Lead Qualification
**Objective**: Customer provides details smoothly, asks about cashless claims, and receives a CRM quote.  
**Status**: `QUALIFIED` | **Lead Quotation**: `LEAD-2026-0005`  
**Citations Used**: `kb_qualification_003`, `kb_policy_003`, `kb_faq_001`, `kb_policy_012`

## Call Dialogue & Diarization

- **Agent (Sarah)** [`turn_00_greeting.mp3`]: "Hello! Thank you for calling ApexCare Health Insurance. My name is Sarah. Are you looking to explore coverage options for yourself or your family today?"
- **User** [`turn_01_user.mp3`]: "Hello, my name is David. I am 34 years old looking for health insurance."
- **Agent (Sarah)** [`turn_01_agent.mp3`]: "Hello, David! Thank you for contacting ApexCare Health. My name is Sarah. It's a pleasure to help you explore health coverage options today. 

To help me find the best plan for you, could you let me know if you have any pre-existing medical conditions, such as hypertension or asthma, and whether you have a preferred coverage tier or budget in mind like our Bronze, Silver, or Gold plans?"
- **User** [`turn_02_user.mp3`]: "I have no pre-existing conditions, totally healthy."
- **Agent (Sarah)** [`turn_02_agent.mp3`]: "That's wonderful to hear, David! Being in great health opens up some fantastic options for you. To help me find the best fit, are you leaning toward a specific budget or coverage tier like our Bronze, Silver, or Gold plans?" *(Grounding: kb_qualification_003, kb_policy_003)*
- **User** [`turn_03_user.mp3`]: "I think Silver tier sounds good. How do I file a cashless claim at a network hospital?"
- **Agent (Sarah)** [`turn_03_agent.mp3`]: "Wonderful choice, David! The Silver tier is a fantastic, balanced option. 

To file a cashless claim at a network hospital, simply present your digital member ID card at the hospital's insurance desk at least 48 hours before a planned admission—or within 24 hours in an emergency—and our claims desk will review and approve eligible expenses within 60 minutes." *(Grounding: kb_faq_001, kb_policy_012)*
- **User** [`turn_04_user.mp3`]: "That sounds great, please lock in my preliminary quotation."
- **Agent (Sarah)** [`turn_04_agent.mp3`]: "That's wonderful, David! I have noted your preference for the Silver plan, and I'll go ahead and generate your official preliminary quotation right now. Let me just get your email address so I can send the complete policy breakdown directly to your inbox."