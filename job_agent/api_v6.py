from fastapi import APIRouter
from .db import get_jobs
from .copilot import load_profile
from .recruiter import recruiter_brief, follow_up_message
from .interview import analyze_feedback, interview_plan
from .v6db import add_contact, add_outreach, add_interview, add_outcome, due_followups
from .learning_v6 import outcome_report, calibration

router=APIRouter(prefix='/v6', tags=['v6'])

@router.post('/contacts')
def contact(payload: dict): return {'id': add_contact(**payload)}

@router.get('/jobs/{job_id}/recruiter-brief')
def recruiter(job_id: str):
    jobs=[j for j in get_jobs(limit=10000) if j['job_id']==job_id]
    if not jobs: return {'error':'job not found'}
    p=load_profile(); return recruiter_brief(jobs[0],p)

@router.post('/outreach')
def outreach(payload: dict): return {'id': add_outreach(**payload)}

@router.post('/interviews')
def interview(payload: dict):
    feedback=payload.get('feedback','')
    analysis=analyze_feedback(feedback)
    payload['analysis_json']=__import__('json').dumps(analysis)
    return {'id': add_interview(**payload), 'analysis':analysis}

@router.get('/jobs/{job_id}/interview-plan')
def plan(job_id: str):
    jobs=[j for j in get_jobs(limit=10000) if j['job_id']==job_id]
    if not jobs: return {'error':'job not found'}
    return interview_plan(jobs[0])

@router.post('/outcomes')
def outcome(payload: dict): return {'id': add_outcome(**payload)}

@router.get('/followups')
def followups(): return due_followups()

@router.get('/outcomes/report')
def report(): return outcome_report()

@router.get('/outcomes/calibration')
def cal(): return calibration()
