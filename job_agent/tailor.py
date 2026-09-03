from __future__ import annotations
import os, json, httpx

PROMPT='''Tailor this resume for the supplied job description. Preserve truthfulness: never invent employers, projects, metrics, dates, certifications, or skills. Return JSON with keys summary, skills_to_emphasize, bullets_to_rewrite, keywords_to_add_if_true, gaps. Keep the candidate's original facts.''' 

def tailor_resume(resume_text: str, job: dict):
    url=os.getenv('OLLAMA_URL','http://localhost:11434')
    model=os.getenv('OLLAMA_MODEL','qwen2.5:7b')
    payload={'model':model,'prompt':PROMPT+'\nRESUME:\n'+resume_text+'\nJOB:\n'+json.dumps(job)[:18000], 'stream':False,'format':'json'}
    r=httpx.post(f'{url}/api/generate',json=payload,timeout=60); r.raise_for_status()
    return json.loads(r.json()['response'])
