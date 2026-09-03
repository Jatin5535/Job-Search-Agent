from __future__ import annotations
from fastapi import APIRouter, HTTPException
from .db import get_jobs
from .copilot import load_profile, application_brief
from .webintel import public_signals
from .decisioning import application_quality

router=APIRouter(prefix='/copilot',tags=['copilot'])

@router.get('/job/{job_id}')
def brief(job_id:str):
    jobs=get_jobs(limit=10000)
    row=next((x for x in jobs if x['job_id']==job_id),None)
    if not row: raise HTTPException(404,'job not found')
    p=load_profile(); b=application_brief(row,p); wi=public_signals(row); q=application_quality(row,b,int(row.get('score',0)))
    return {'job':row,'brief':b,'web_intel':wi,'decision':q}
