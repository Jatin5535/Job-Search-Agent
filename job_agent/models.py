from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass
class Job:
    job_id: str
    source: str
    company: str
    title: str
    location: str
    workplace_type: str
    url: str
    apply_url: str
    description: str
    posted_at: Optional[str] = None
    salary: Optional[str] = None
    department: Optional[str] = None
    raw: Optional[dict] = None
