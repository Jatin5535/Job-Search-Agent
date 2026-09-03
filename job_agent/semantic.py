from __future__ import annotations
import os, json, re
from typing import Optional
import httpx

OLLAMA_URL = os.getenv('OLLAMA_URL','http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL','qwen2.5:7b')

SYSTEM = '''You are a strict job matching engine. Score a job for the candidate profile from 0-100. Do not invent candidate skills. Return JSON only: {"score": number, "verdict": "APPLY|REVIEW|SKIP", "why": [string], "gaps": [string], "red_flags": [string]}'''

def ollama_score(job: dict, profile: dict) -> Optional[dict]:
    prompt = SYSTEM + '\nCANDIDATE:\n' + json.dumps(profile, ensure_ascii=False) + '\nJOB:\n' + json.dumps(job, ensure_ascii=False)[:18000]
    try:
        r = httpx.post(f'{OLLAMA_URL}/api/generate', json={'model':OLLAMA_MODEL,'prompt':prompt,'stream':False,'format':'json'}, timeout=45)
        r.raise_for_status()
        return json.loads(r.json().get('response','{}'))
    except Exception:
        return None

def keyword_explanation(job, profile):
    text=(job.get('title','')+' '+job.get('description','')).lower()
    skills=profile.get('must_have_skills',[])+profile.get('strong_skills',[])
    hits=[s for s in skills if s.lower() in text]
    return hits
