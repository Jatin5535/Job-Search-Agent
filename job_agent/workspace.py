from __future__ import annotations
import json
from datetime import datetime, timezone
from typing import Any
from .db import connect, get_jobs
from .apply_copilot import build_apply_pack
from .decisioning import application_quality
from .copilot import application_brief, load_profile
from .recruiter import recruiter_brief
from .interview import interview_plan

_ALLOWED = {'new','review','applied','screening','interview','offer','rejected','withdrawn'}


def _decision_guard(job: dict[str, Any]) -> dict[str, Any]:
    score = int(job.get('score') or 0)
    verdict = str(job.get('verdict') or 'SKIP').upper()
    expected = 'APPLY' if score >= 90 else 'REVIEW' if score >= 78 else 'SKIP'
    return {'consistent': verdict == expected, 'expected': expected, 'actual': verdict, 'score': score}


def _job(job_id: str) -> dict[str, Any]:
    jobs = [j for j in get_jobs(limit=10000) if j['job_id'] == job_id]
    if not jobs:
        raise KeyError(job_id)
    return jobs[0]


def build_workspace(job_id: str) -> dict[str, Any]:
    profile = load_profile()
    job = _job(job_id)
    guard = _decision_guard(job)
    brief = application_brief(job, profile)
    quality = application_quality(job, brief, int(job.get('score') or 0))
    apply_pack = build_apply_pack(job_id, profile)
    recruiter = recruiter_brief(job, profile)
    interview = interview_plan(job)
    return {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'decision_guard': guard,
        'job': {k: job.get(k) for k in ('job_id','company','title','location','workplace_type','url','apply_url','source','score','semantic_score','verdict','status','salary')},
        'recommendation': quality,
        'application': apply_pack,
        'recruiter': recruiter,
        'interview': interview,
        'next_actions': [
            'Review the recommendation and all generated claims.',
            'Open the application URL and submit manually.',
            'Record the application status and recruiter outreach.',
            'Add interview feedback after every round.',
        ]
    }
