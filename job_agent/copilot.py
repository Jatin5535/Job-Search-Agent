from __future__ import annotations
import re
from pathlib import Path
from typing import Any
import yaml

STOP = {"and","the","for","with","from","that","this","you","your","are","our","job","role","will","have","has","into","about","must","years","year","work","team","using","use","build","building","strong","experience","skills","required","preferred","plus","looking","candidate"}

def _tokens(text: str) -> set[str]:
    return {x for x in re.findall(r"[a-z0-9][a-z0-9+.#/-]{1,}", (text or '').lower()) if x not in STOP}

def load_profile(path='config/profile.yaml') -> dict[str, Any]:
    with open(path, encoding='utf-8') as f:
        return yaml.safe_load(f)['profile']

def _resume_text(profile: dict[str, Any]) -> str:
    chunks=[]
    for k in ('headline','summary','must_have_skills','strong_skills','nice_to_have_skills','target_titles','preferred_locations'):
        v=profile.get(k,'')
        if isinstance(v,list): chunks.extend(map(str,v))
        else: chunks.append(str(v))
    p=profile.get('resume_path')
    if p and Path(p).exists():
        chunks.append(Path(p).read_text(encoding='utf-8',errors='ignore'))
    return ' '.join(chunks)

def application_brief(job: dict[str,Any], profile: dict[str,Any]) -> dict[str,Any]:
    jd=(job.get('title','')+' '+job.get('description','')).strip()
    resume=_resume_text(profile)
    jt=_tokens(job.get('title',''))
    rt=_tokens(resume)
    dt=_tokens(jd)
    exact=sorted((dt & rt) - STOP, key=lambda x:(-len(x),x))
    skill_hits=[]
    for s in profile.get('must_have_skills',[])+profile.get('strong_skills',[]):
        if s.lower() in jd.lower(): skill_hits.append(s)
    gaps=[s for s in profile.get('must_have_skills',[]) if s.lower() not in jd.lower()]
    missing_resume=[s for s in skill_hits if s.lower() not in resume.lower()]
    focus=skill_hits[:8] or exact[:8]
    return {
        'company': job.get('company'), 'title': job.get('title'),
        'application_angle': f"Lead with {', '.join(focus[:5])}" if focus else 'Lead with your strongest directly relevant production AI/cloud work.',
        'matched_signals': skill_hits[:12],
        'resume_emphasis': focus[:10],
        'possible_gaps': gaps[:8],
        'verify_before_claiming': missing_resume[:8],
        'cover_note': f"Hello, I’m interested in the {job.get('title','')} role at {job.get('company','your company')}. My background in {', '.join(focus[:4]) if focus else 'AI engineering and cloud solutions'} aligns well with the position. I’d welcome the opportunity to discuss how I can contribute.",
        'interview_questions': [f"Walk me through your most relevant experience with {x}." for x in focus[:5]],
        'checklist': ['Open the job description and verify hard requirements', 'Review the tailored resume before submission', 'Confirm location/work authorization requirements', 'Apply manually only after review']
    }
