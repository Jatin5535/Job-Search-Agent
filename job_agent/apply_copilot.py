from __future__ import annotations
import json, re
from typing import Any
from .copilot import application_brief
from .db import connect, set_status

PLATFORM_HINTS = {
    'linkedin': ('linkedin.com/jobs', 'linkedin.com/job'),
    'naukri': ('naukri.com/job-listings', 'naukri.com/jobs'),
}

def detect_platform(url: str, source: str = '') -> str:
    u=(url or '').lower()
    s=(source or '').lower()
    if any(x in u for x in PLATFORM_HINTS['linkedin']) or 'linkedin' in s:
        return 'linkedin'
    if any(x in u for x in PLATFORM_HINTS['naukri']) or 'naukri' in s:
        return 'naukri'
    return 'other'

def get_job(job_id: str):
    with connect() as con:
        row=con.execute('SELECT * FROM jobs WHERE job_id=?',(job_id,)).fetchone()
        return dict(row) if row else None

def build_apply_pack(job_id: str, profile: dict[str,Any]) -> dict[str,Any]:
    job=get_job(job_id)
    if not job:
        raise KeyError(job_id)
    try: job['raw']=json.loads(job.get('raw_json') or '{}')
    except Exception: job['raw']={}
    brief=application_brief(job, profile)
    platform=detect_platform(job.get('apply_url') or job.get('url'), job.get('source'))
    # Only suggest truthful, generic application answers. The user should review these before submission.
    answers={
        'full_name': profile.get('full_name',''),
        'email': profile.get('email',''),
        'phone': profile.get('phone',''),
        'years_experience': str(profile.get('years_experience','')),
        'current_title': profile.get('headline',''),
        'location': profile.get('current_location','India'),
        'work_authorization': profile.get('work_authorization',''),
        'notice_period': profile.get('notice_period',''),
        'linkedin_url': profile.get('linkedin_url',''),
        'github_url': profile.get('github_url',''),
        'portfolio_url': profile.get('portfolio_url',''),
    }
    answer_text='\n'.join(f'{k.replace("_"," ").title()}: {v}' for k,v in answers.items() if v)
    return {
        'job': {k:job.get(k) for k in ('job_id','company','title','location','workplace_type','apply_url','url','source','score','verdict','status')},
        'platform': platform,
        'mode': 'assisted_manual_submit',
        'compliance_note': 'Opens the public job/application page and prepares content for review. It does not log in, scrape authenticated pages, bypass controls, or click Submit.',
        'answers': answers,
        'answer_text': answer_text,
        'application_brief': brief,
        'submit_checklist': [
            'Open the application link.',
            'Review every prefilled field and qualification answer.',
            'Attach the intended resume and any requested documents.',
            'Review AI-generated text for accuracy and truthful claims.',
            'Submit the application yourself.',
            'Return to the dashboard and mark the job as Applied.'
        ]
    }

def mark_applied(job_id: str):
    set_status(job_id, 'applied')
    return {'ok':True,'job_id':job_id,'status':'applied'}
