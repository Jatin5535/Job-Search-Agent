from __future__ import annotations
from collections import Counter
from .db import connect

def learned_adjustment(job: dict, profile: dict) -> tuple[int,list[str]]:
    """Small bounded preference-learning signal based on explicit user feedback and outcomes."""
    with connect() as con:
        rows=con.execute("SELECT f.action,f.value,j.company FROM feedback f JOIN jobs j ON j.job_id=f.job_id ORDER BY f.created_at DESC LIMIT 500").fetchall()
    if not rows: return 0, []
    title=(job.get('title') or '').lower(); company=(job.get('company') or '').lower(); body=(title+' '+(job.get('description') or '')).lower()
    adj=0; reasons=[]
    positive_terms=Counter(); negative_terms=Counter(); company_scores={}
    for r in rows:
        val=float(r['value']); act=r['action']
        if act in {'like','shortlist','applied','interview','offer'} and val>0: sign=1
        elif act in {'skip','reject'} and val<0: sign=-1
        else: sign=1 if val>0 else -1
        for token in title.split():
            if len(token)>=4:
                (positive_terms if sign>0 else negative_terms)[token]+=1
        c=(r['company'] or '').lower(); company_scores[c]=company_scores.get(c,0)+sign
    overlap=sum(1 for t,n in positive_terms.items() if n>=2 and t in title)
    oppose=sum(1 for t,n in negative_terms.items() if n>=2 and t in title)
    if overlap: adj += min(4,overlap); reasons.append(f'Learned preference signal (+{min(4,overlap)})')
    if oppose: adj -= min(4,oppose); reasons.append(f'Learned avoidance signal (-{min(4,oppose)})')
    cs=company_scores.get(company,0)
    if cs>1: adj += min(4,cs); reasons.append('Positive history with this company (+2..4)')
    elif cs<0: adj -= min(4,abs(cs)); reasons.append('Negative history with this company (-1..4)')
    return max(-8,min(8,adj)), reasons
