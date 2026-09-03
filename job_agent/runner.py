from __future__ import annotations
from .config import profile, sources
from .collectors import collect_all
from .db import init_db, upsert_job
from .scorer import score_job


def run_scan():
    init_db()
    jobs, errors = collect_all(sources())
    saved = 0
    for job in jobs:
        score, reasons = score_job(job, profile())
        upsert_job(job, score, reasons)
        saved += 1
    return {"collected": len(jobs), "saved": saved, "errors": errors}
