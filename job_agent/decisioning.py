from __future__ import annotations
from typing import Any

def application_quality(job: dict[str,Any], brief: dict[str,Any], score: int) -> dict[str,Any]:
    deductions=[]
    if brief.get('verify_before_claiming'): deductions.append(('claim-verification', 5))
    if brief.get('possible_gaps'): deductions.append(('requirement-gap', min(10, 2*len(brief['possible_gaps']))))
    risks=job.get('risks') or []
    if any('citizen' in str(x).lower() or 'clearance' in str(x).lower() for x in risks): deductions.append(('eligibility-risk', 15))
    q=max(0, score-sum(v for _,v in deductions))
    action='APPLY' if q>=90 else 'REVIEW' if q>=78 else 'SKIP'
    return {'quality_score':q,'recommended_action':action,'deductions':deductions}
