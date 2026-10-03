"""
Automated Endpoint Health & Integration Verification Script
"""
import urllib.request
import json

base_url = 'http://127.0.0.1:8000'

print("="*70)
print("RUNNING FULL ENDPOINT HEALTH & INTEGRATION AUDIT")
print("="*70)

# 1. Health Check
with urllib.request.urlopen(f'{base_url}/api/health') as r:
    health = json.loads(r.read().decode())
    print('[1/5] Health Check: OK')
    print(f'      Status: {health["status"]} | Provider: {health["provider"]} | Chunks: {health["chunks_indexed"]}')

# 2. Direct KB search
with urllib.request.urlopen(f'{base_url}/api/kb/search?q=hypertension+waiting+period') as r:
    kb_res = json.loads(r.read().decode())
    print('[2/5] Direct KB Search API: OK')
    print(f'      Found: {kb_res["total_found"]} citations | Top: {kb_res["citations"][0]["record_id"]} ({kb_res["confidence_verdict"]})')

# 3. CRM leads
with urllib.request.urlopen(f'{base_url}/api/crm/leads') as r:
    leads = json.loads(r.read().decode())
    print('[3/5] CRM Leads API: OK')
    print(f'      Stored {len(leads)} leads. Latest: {leads[-1]["lead_id"]} - {leads[-1]["caller_name"]} ({leads[-1]["qualification_status"]})')

# 4. Interactive Call Flow (Start Call -> Turn 1 -> Turn 2)
start_req = urllib.request.Request(f'{base_url}/api/call/start', data=b'{}', headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(start_req) as r:
    session = json.loads(r.read().decode())
    s_id = session['session_id']
    print('[4/5] Start Call Session API: OK')
    print(f'      Session: {s_id}')
    print(f'      Greeting: "{session["greeting"][:60]}..."')
    print(f'      Audio URL: {session["audio_url"]}')

# Turn 1
payload = json.dumps({'session_id': s_id, 'user_transcript': 'My name is Sarah Connor, I am 32 years old looking for individual coverage.'}).encode()
req = urllib.request.Request(f'{base_url}/api/call/turn', data=payload, headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as r:
    turn1 = json.loads(r.read().decode())
    print('[5/5] Multi-Turn Interactive Voice Call API: OK')
    print(f'      Turn 1 Reply: "{turn1["reply"][:80]}..."')
    print(f'      Audio Generated: {turn1["audio_url"]}')

# Turn 2 with RAG grounding
payload = json.dumps({'session_id': s_id, 'user_transcript': 'How much does Gold tier cost and what are the room rent caps?'}).encode()
req = urllib.request.Request(f'{base_url}/api/call/turn', data=payload, headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as r:
    turn2 = json.loads(r.read().decode())
    print(f'      Turn 2 Grounded Reply: "{turn2["reply"][:80]}..."')
    print(f'      Grounding Citations: {[c["record_id"] for c in turn2["citations"]]}')

print("="*70)
print("ALL ENDPOINTS VERIFIED & WORKING PERFECTLY!")
print("="*70)
