from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Any

@dataclass
class Analysis:
    score: int
    verdict: str
    matched: list[str]
    gaps: list[str]
    why_apply: list[str]
    risks: list[str]
    interview_focus: list[str]


def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip().lower()


def extract_years(text: str) -> tuple[int|None,int|None]:
    t = normalize(text)
    vals=[]
    for m in re.finditer(r"(\d+)\s*(?:\+|to|-)?\s*(\d+)?\s*years?", t):
        vals.append(int(m.group(1)))
        if m.group(2): vals.append(int(m.group(2)))
    return (min(vals), max(vals)) if vals else (None,None)


def advanced_score(job: dict[str,Any], profile: dict[str,Any], base_score: int) -> Analysis:
    body = normalize((job.get('title','')+' '+job.get('description','')))
    must = profile.get('must_have_skills',[])
    strong = profile.get('strong_skills',[])
    nice = profile.get('nice_to_have_skills',[])
    matched=[]; gaps=[]
    for skill in must+strong+nice:
        if normalize(skill) in body:
            matched.append(skill)
    for skill in must:
        if normalize(skill) not in body:
            gaps.append(skill)

    score = base_score
    # High-signal adjustments (capped so deterministic score remains primary)
    if any(k in body for k in ['production', 'customer-facing', 'enterprise']): score += 3
    if any(k in body for k in ['visa sponsorship', 'relocation assistance']): score += 2
    if any(k in body for k in ['security clearance', 'must be a us citizen', 'us citizenship required']): score -= 10
    if gaps: score -= min(8, len(gaps)*2)
    score=max(0,min(100,score))
    verdict='APPLY' if score>=90 else 'REVIEW' if score>=78 else 'SKIP'
    why=[]
    if matched: why.append('Strong overlap with your listed skills: '+', '.join(matched[:8]))
    if any(x in body for x in ['architecture','architect','design systems']): why.append('Architecture/design exposure is relevant')
    if 'remote' in body: why.append('Remote work is mentioned in the role')
    if not why: why.append('Role has some alignment, but the fit is not highly specific')
    risks=[]
    if gaps: risks.append('Missing/unclear must-have signals: '+', '.join(gaps))
    if score < 70: risks.append('Overall fit is below the target threshold')
    interview=[]
    for skill in matched[:5]: interview.append(f'Be ready to discuss {skill} with a concrete project example')
    return Analysis(score,verdict,matched,gaps,why,risks,interview)
