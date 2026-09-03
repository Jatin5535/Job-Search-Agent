from __future__ import annotations
import sqlite3
from datetime import datetime, timezone
from .db import connect


def init_v6():
    with connect() as con:
        con.executescript('''
        CREATE TABLE IF NOT EXISTS recruiter_contacts (
          id INTEGER PRIMARY KEY AUTOINCREMENT, company TEXT NOT NULL, name TEXT, role TEXT,
          channel TEXT, profile_url TEXT, email TEXT, notes TEXT, created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS outreach (
          id INTEGER PRIMARY KEY AUTOINCREMENT, job_id TEXT NOT NULL, contact_id INTEGER,
          channel TEXT NOT NULL, message TEXT, sent_at TEXT, response_at TEXT, outcome TEXT,
          follow_up_at TEXT, notes TEXT
        );
        CREATE TABLE IF NOT EXISTS interview_notes (
          id INTEGER PRIMARY KEY AUTOINCREMENT, job_id TEXT NOT NULL, round_name TEXT,
          scheduled_at TEXT, completed_at TEXT, feedback TEXT, analysis_json TEXT,
          next_step TEXT, created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS outcomes (
          id INTEGER PRIMARY KEY AUTOINCREMENT, job_id TEXT NOT NULL, outcome TEXT NOT NULL,
          reason TEXT, created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_outreach_followup ON outreach(follow_up_at);
        CREATE INDEX IF NOT EXISTS idx_interview_job ON interview_notes(job_id);
        ''')


def add_contact(company, name='', role='', channel='', profile_url='', email='', notes=''):
    with connect() as con:
        cur=con.execute('INSERT INTO recruiter_contacts(company,name,role,channel,profile_url,email,notes,created_at) VALUES(?,?,?,?,?,?,?,?)',
                        (company,name,role,channel,profile_url,email,notes,datetime.now(timezone.utc).isoformat()))
        con.commit(); return cur.lastrowid


def add_outreach(job_id, channel, message, contact_id=None, sent_at=None, follow_up_at=None, notes=''):
    with connect() as con:
        cur=con.execute('INSERT INTO outreach(job_id,contact_id,channel,message,sent_at,follow_up_at,notes) VALUES(?,?,?,?,?,?,?)',
                        (job_id,contact_id,channel,message,sent_at,follow_up_at,notes))
        con.commit(); return cur.lastrowid


def add_interview(job_id, round_name, scheduled_at=None, completed_at=None, feedback='', analysis_json='', next_step=''):
    with connect() as con:
        cur=con.execute('INSERT INTO interview_notes(job_id,round_name,scheduled_at,completed_at,feedback,analysis_json,next_step,created_at) VALUES(?,?,?,?,?,?,?,?)',
                        (job_id,round_name,scheduled_at,completed_at,feedback,analysis_json,next_step,datetime.now(timezone.utc).isoformat()))
        con.commit(); return cur.lastrowid


def add_outcome(job_id, outcome, reason=''):
    with connect() as con:
        cur=con.execute('INSERT INTO outcomes(job_id,outcome,reason,created_at) VALUES(?,?,?,?)',
                        (job_id,outcome,reason,datetime.now(timezone.utc).isoformat()))
        con.commit(); return cur.lastrowid


def due_followups(now_iso=None):
    now_iso=now_iso or datetime.now(timezone.utc).isoformat()
    with connect() as con:
        return [dict(r) for r in con.execute('SELECT * FROM outreach WHERE follow_up_at IS NOT NULL AND follow_up_at<=? AND (response_at IS NULL OR response_at="") ORDER BY follow_up_at', (now_iso,)).fetchall()]
