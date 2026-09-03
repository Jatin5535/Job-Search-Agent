from __future__ import annotations
from fastapi import FastAPI, Query
from .db import init_db,get_jobs,set_status,add_feedback,feedback_summary
from .pipeline import run_scan
from .copilot_api import router as copilot_router
from .api_v6 import router as v6_router
from .apply_api import router as apply_router
from .workspace_api import router as workspace_router
from .v6db import init_v6
import json
app=FastAPI(title='Career Control Tower V8',version='8.0.0')
app.include_router(copilot_router)
app.include_router(v6_router)
app.include_router(apply_router)
app.include_router(workspace_router)
init_db(); init_v6()
@app.get('/health')
def health(): return {'ok':True,'version':'8.0.0'}
@app.post('/run')
def run():
    n,e=run_scan(); return {'jobs_found':n,'errors':e}
@app.get('/jobs')
def jobs(limit:int=Query(50,ge=1,le=1000),min_score:int=Query(0,ge=0,le=100),status:str='all'):
    out=get_jobs(limit,min_score,status)
    for d in out:
        for k in ('reasons','matched','gaps','risks'):
            try:d[k]=json.loads(d[k] or '[]')
            except:pass
        try:d['raw']=json.loads(d.pop('raw_json') or '{}')
        except:d.pop('raw_json',None)
    return out
@app.post('/jobs/{job_id}/status/{status}')
def update(job_id:str,status:str): set_status(job_id,status); return {'ok':True}
@app.post('/jobs/{job_id}/feedback')
def feedback(job_id:str,action:str,value:float,note:str=''): add_feedback(job_id,action,value,note); return {'ok':True}
@app.get('/feedback-summary')
def fs(): return feedback_summary()
