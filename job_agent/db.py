from __future__ import annotations
import json, sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from .models import Job

DB_PATH = Path("data/jobs.db")
STATUSES = {'new','review','applied','screening','interview','offer','rejected','withdrawn'}

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
 job_id TEXT PRIMARY KEY, source TEXT NOT NULL, company TEXT NOT NULL, title TEXT NOT NULL,
 location TEXT, workplace_type TEXT, url TEXT NOT NULL, apply_url TEXT, description TEXT,
 posted_at TEXT, salary TEXT, department TEXT, score INTEGER DEFAULT 0, semantic_score INTEGER,
 verdict TEXT DEFAULT 'SKIP', reasons TEXT DEFAULT '[]', matched TEXT DEFAULT '[]', gaps TEXT DEFAULT '[]',
 risks TEXT DEFAULT '[]', first_seen_at TEXT NOT NULL, last_seen_at TEXT NOT NULL,
 status TEXT DEFAULT 'new', raw_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_jobs_score ON jobs(score DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);
CREATE TABLE IF NOT EXISTS feedback (
 id INTEGER PRIMARY KEY AUTOINCREMENT, job_id TEXT NOT NULL, action TEXT NOT NULL,
 value REAL NOT NULL, note TEXT, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS company_signals (
 company TEXT PRIMARY KEY, positive INTEGER DEFAULT 0, negative INTEGER DEFAULT 0,
 applied INTEGER DEFAULT 0, interview INTEGER DEFAULT 0, offer INTEGER DEFAULT 0, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS search_runs (
 id INTEGER PRIMARY KEY AUTOINCREMENT, started_at TEXT NOT NULL, finished_at TEXT,
 jobs_found INTEGER DEFAULT 0, new_jobs INTEGER DEFAULT 0, high_matches INTEGER DEFAULT 0, errors TEXT DEFAULT '[]'
);
"""

@contextmanager
def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        yield con
    finally:
        con.close()

def init_db():
    with connect() as con: con.executescript(SCHEMA)

def upsert_job(job: Job, score: int, reasons: list[str], *, semantic_score=None, verdict='SKIP', matched=None, gaps=None, risks=None):
    now=datetime.now(timezone.utc).isoformat()
    with connect() as con:
        exists = con.execute("SELECT 1 FROM jobs WHERE job_id=?", (job.job_id,)).fetchone() is not None
        con.execute("""INSERT INTO jobs
        (job_id,source,company,title,location,workplace_type,url,apply_url,description,posted_at,salary,department,score,semantic_score,verdict,reasons,matched,gaps,risks,first_seen_at,last_seen_at,raw_json)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(job_id) DO UPDATE SET company=excluded.company,title=excluded.title,location=excluded.location,
        workplace_type=excluded.workplace_type,url=excluded.url,apply_url=excluded.apply_url,description=excluded.description,
        posted_at=excluded.posted_at,salary=excluded.salary,department=excluded.department,score=excluded.score,
        semantic_score=excluded.semantic_score,verdict=excluded.verdict,reasons=excluded.reasons,matched=excluded.matched,
        gaps=excluded.gaps,risks=excluded.risks,last_seen_at=excluded.last_seen_at,raw_json=excluded.raw_json""",
        (job.job_id,job.source,job.company,job.title,job.location,job.workplace_type,job.url,job.apply_url,job.description,
         job.posted_at,job.salary,job.department,score,semantic_score,verdict,json.dumps(reasons),json.dumps(matched or []),
         json.dumps(gaps or []),json.dumps(risks or []),now,now,json.dumps(job.raw or {},ensure_ascii=False)))
        con.commit()
    return not exists

def get_jobs(limit=1000, min_score=0, status='all'):
    with connect() as con:
        q="SELECT * FROM jobs WHERE score>=?"; args=[min_score]
        if status!='all': q += " AND status=?"; args.append(status)
        q += " ORDER BY score DESC, first_seen_at DESC LIMIT ?"; args.append(limit)
        rows=[dict(r) for r in con.execute(q,args).fetchall()]
        for d in rows:
            for k in ('reasons','matched','gaps','risks'):
                try: d[k]=json.loads(d.get(k) or '[]')
                except (TypeError, json.JSONDecodeError): d[k]=[]
        return rows

def set_status(job_id,status):
    if status not in STATUSES: raise ValueError(status)
    with connect() as con:
        con.execute("UPDATE jobs SET status=? WHERE job_id=?",(status,job_id)); con.commit()
        company=con.execute("SELECT company FROM jobs WHERE job_id=?",(job_id,)).fetchone()
        if company:
            c=company['company']; now=datetime.now(timezone.utc).isoformat()
            con.execute("INSERT INTO company_signals(company,updated_at) VALUES(?,?) ON CONFLICT(company) DO UPDATE SET updated_at=excluded.updated_at",(c,now))
            if status=='applied': con.execute("UPDATE company_signals SET applied=applied+1 WHERE company=?",(c,))
            if status=='interview': con.execute("UPDATE company_signals SET interview=interview+1 WHERE company=?",(c,))
            if status=='offer': con.execute("UPDATE company_signals SET offer=offer+1 WHERE company=?",(c,))
            con.commit()

def add_feedback(job_id,action,value,note=''):
    with connect() as con:
        con.execute("INSERT INTO feedback(job_id,action,value,note,created_at) VALUES(?,?,?,?,?)",(job_id,action,float(value),note,datetime.now(timezone.utc).isoformat())); con.commit()

def company_signal(company):
    with connect() as con:
        row=con.execute("SELECT * FROM company_signals WHERE company=?",(company,)).fetchone()
        return dict(row) if row else None

def feedback_summary():
    with connect() as con:
        return [dict(r) for r in con.execute("SELECT action, AVG(value) avg_value, COUNT(*) count FROM feedback GROUP BY action ORDER BY count DESC").fetchall()]

def start_run():
    with connect() as con:
        cur=con.execute("INSERT INTO search_runs(started_at) VALUES(?)",(datetime.now(timezone.utc).isoformat(),)); con.commit(); return cur.lastrowid

def finish_run(run_id, jobs_found, new_jobs, high_matches, errors):
    with connect() as con:
        con.execute("UPDATE search_runs SET finished_at=?,jobs_found=?,new_jobs=?,high_matches=?,errors=? WHERE id=?",(datetime.now(timezone.utc).isoformat(),jobs_found,new_jobs,high_matches,json.dumps(errors),run_id)); con.commit()
