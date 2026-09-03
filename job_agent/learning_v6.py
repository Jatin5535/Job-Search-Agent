from __future__ import annotations
import statistics
from .db import connect


def outcome_report():
    with connect() as con:
        rows=[dict(r) for r in con.execute('''
        SELECT j.company,j.title,j.score,j.status,o.outcome,o.reason
        FROM jobs j JOIN outcomes o ON o.job_id=j.job_id
        ORDER BY o.created_at DESC
        ''').fetchall()]
    return rows


def calibration():
    with connect() as con:
        rows=[dict(r) for r in con.execute('''
        SELECT j.score, j.status, o.outcome
        FROM jobs j JOIN outcomes o ON o.job_id=j.job_id
        WHERE o.outcome IN ('interview','offer','rejected')
        ''').fetchall()]
    buckets={}
    for r in rows:
        b=(int(r['score'])//10)*10
        buckets.setdefault(b, {'scores':[], 'interviews':0, 'offers':0, 'rejected':0})
        buckets[b]['scores'].append(r['score'])
        if r['outcome']=='interview': buckets[b]['interviews']+=1
        if r['outcome']=='offer': buckets[b]['offers']+=1
        if r['outcome']=='rejected': buckets[b]['rejected']+=1
    out=[]
    for b,v in sorted(buckets.items()):
        n=len(v['scores']); out.append({'bucket':b,'n':n,'avg_score':round(statistics.mean(v['scores']),1),'interview_rate':round(v['interviews']/n,3),'offer_rate':round(v['offers']/n,3),'reject_rate':round(v['rejected']/n,3)})
    return out
