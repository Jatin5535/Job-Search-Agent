from __future__ import annotations
import os, json, httpx

PROMPT='''You are a career coach. Given a candidate profile and job description, produce strict JSON with: score_adjustment (-10..10), why_apply (3 concise strings), key_gaps (up to 5), resume_emphasis (up to 7), interview_focus (up to 5), questions_to_verify (up to 5). Never invent candidate experience.''' 

def analyze(job:dict, profile:dict):
    if os.getenv('LLM_ENABLED','false').lower()!='true': return None
    url=os.getenv('OLLAMA_URL','http://localhost:11434'); model=os.getenv('OLLAMA_MODEL','qwen2.5:7b')
    p=PROMPT+'\nCANDIDATE:\n'+json.dumps(profile,ensure_ascii=False)+'\nJOB:\n'+json.dumps(job,ensure_ascii=False)[:22000]
    r=httpx.post(f'{url}/api/generate',json={'model':model,'prompt':p,'stream':False,'format':'json'},timeout=90); r.raise_for_status()
    return json.loads(r.json().get('response','{}'))
