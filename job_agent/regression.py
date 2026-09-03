from __future__ import annotations
import tempfile
from pathlib import Path
from . import db
from .models import Job
from .scorer import score_job
from .workspace import _decision_guard


def run_regression() -> dict:
    original = db.DB_PATH
    with tempfile.TemporaryDirectory() as td:
        db.DB_PATH = Path(td) / 'jobs.db'
        db.init_db()
        profile = {
            'full_name':'Test Candidate','years_experience':2,'headline':'AI Engineer',
            'must_have_skills':['Python','AWS','RAG'],'current_location':'India',
            'target_titles':['AI Engineer','GenAI Engineer'],'preferred_work_modes':['remote'],
            'target_locations':['India'],'llm_enabled':False,
        }
        job = Job(
            job_id='regression-001',source='test',company='Example AI',title='GenAI Engineer',
            location='Remote - India',workplace_type='remote',url='https://example.com/job',
            apply_url='https://example.com/apply',description='Python AWS RAG LLM AI engineer',
            posted_at=None,salary=None,department='AI',raw={}
        )
        score, _ = score_job(job, profile)
        verdict = 'APPLY' if score >= 90 else 'REVIEW' if score >= 78 else 'SKIP'
        result = {'score': score, 'verdict': verdict, 'guard': _decision_guard({'score':score,'verdict':verdict})}
        assert result['guard']['consistent']
        assert 0 <= score <= 100
        db.DB_PATH = original
    return result
