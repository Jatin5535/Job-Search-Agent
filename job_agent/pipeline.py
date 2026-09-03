from __future__ import annotations
import yaml
from .collectors import collect_all
from .email_ingest import ingest_alert_emails
from .db import init_db, upsert_job, start_run, finish_run
from .scorer import score_job
from .advanced import advanced_score
from .learning import learned_adjustment
from .discovery import discover_from_urls
from .semantic import ollama_score

def load_cfg():
    with open('config/profile.yaml',encoding='utf-8') as f: profile=yaml.safe_load(f)['profile']
    with open('config/sources.yaml',encoding='utf-8') as f:
        cfg=yaml.safe_load(f) or {}; sources=cfg.get('sources',[]); career_urls=cfg.get('career_pages',[])
    return profile,sources,career_urls

def run_scan():
    init_db(); profile,sources,career_urls=load_cfg(); run_id=start_run(); errors=[]
    jobs,_errors=collect_all(sources); errors.extend(_errors)
    try: jobs.extend(ingest_alert_emails())
    except Exception as exc: errors.append(f'email: {exc}')
    jobs.extend(discover_from_urls(career_urls))
    new=0; high=0
    for job in jobs:
        base,reasons=score_job(job,profile)
        a=advanced_score(job.__dict__,profile,base)
        learn,learn_reasons=learned_adjustment(job.__dict__,profile)
        semantic=None
        if profile.get('llm_enabled'):
            semantic=ollama_score(job.__dict__,profile)
        final=a.score+learn
        if semantic and isinstance(semantic.get('score'),(int,float)):
            final=round(final*0.75+float(semantic['score'])*0.25)
            reasons += ['Optional AI semantic score blended (25%)']
        final=max(0,min(100,int(final)))
        if final>=90: verdict='APPLY'
        elif final>=78: verdict='REVIEW'
        else: verdict='SKIP'
        all_reasons=reasons+[f'Verdict: {verdict}']+a.why_apply+a.risks+learn_reasons
        inserted=upsert_job(job,final,all_reasons,semantic_score=(semantic or {}).get('score') if semantic else None,verdict=verdict,matched=a.matched,gaps=a.gaps,risks=a.risks)
        if inserted: new += 1
        if final>=90: high+=1
    finish_run(run_id,len(jobs),new,high,errors)
    return len(jobs), errors
