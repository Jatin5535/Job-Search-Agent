from __future__ import annotations
import argparse, json
from .pipeline import run_scan
from .copilot import load_profile, application_brief
from .db import init_db,get_jobs,set_status,add_feedback,feedback_summary

def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest='cmd',required=True)
    sub.add_parser('scan')
    s=sub.add_parser('shortlist'); s.add_argument('--limit',type=int,default=25); s.add_argument('--min-score',type=int,default=80)
    st=sub.add_parser('status'); st.add_argument('job_id'); st.add_argument('value')
    fb=sub.add_parser('feedback'); fb.add_argument('job_id'); fb.add_argument('action'); fb.add_argument('value',type=float); fb.add_argument('--note',default='')
    sub.add_parser('feedback-summary')
    a=p.parse_args(); init_db()
    if a.cmd=='scan': print(run_scan())
    elif a.cmd=='shortlist':
        for j in get_jobs(a.limit,a.min_score): print(json.dumps(j,ensure_ascii=False))
    elif a.cmd=='status': set_status(a.job_id,a.value); print('updated')
    elif a.cmd=='feedback': add_feedback(a.job_id,a.action,a.value,a.note); print('feedback saved')
    elif a.cmd=='feedback-summary': print(json.dumps(feedback_summary(),indent=2))
if __name__=='__main__': main()
