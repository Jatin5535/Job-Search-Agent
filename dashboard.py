import os
import streamlit as st, requests
from job_agent.db import get_jobs, init_db
from job_agent.pipeline import run_scan
from job_agent.workspace import build_workspace

for secret_name in ('IMAP_HOST', 'IMAP_USER', 'IMAP_PASSWORD', 'IMAP_FROM'):
    if secret_name not in os.environ and secret_name in st.secrets:
        os.environ[secret_name] = str(st.secrets[secret_name])

st.set_page_config(page_title='Career Control Tower V8', layout='wide')
st.title('Career Control Tower V8')
init_db()
base=st.text_input('API URL', os.getenv('API_URL', ''))
if st.button('Run public job scan'):
    try:
        if base.strip():
            result=requests.post(f'{base.rstrip("/")}/run',timeout=90).json()
        else:
            found, errors=run_scan()
            result={'jobs_found': found, 'errors': errors}
        st.success(f"Scan complete: {result.get('jobs_found', 0)} jobs found.")
        if result.get('errors'):
            st.warning('; '.join(result['errors']))
    except (requests.RequestException, OSError) as e:
        st.error(f'Scan failed: {e}')
min_score=st.slider('Minimum score',0,100,78)
status=st.selectbox('Status',['all','new','review','applied','screening','interview','offer','rejected','withdrawn'])
limit=st.number_input('Max jobs',10,500,100)

params={'limit':int(limit),'min_score':min_score,'status':status}
if base.strip():
    try:
        jobs=requests.get(f'{base.rstrip("/")}/jobs',params=params,timeout=10).json()
    except requests.RequestException as e:
        st.warning(f'API unavailable; showing local jobs: {e}')
        jobs=get_jobs(**params)
else:
    jobs=get_jobs(**params)

st.metric('Visible opportunities',len(jobs))
for j in jobs:
    with st.container(border=True):
        a,b,c=st.columns([6,2,2])
        a.markdown(f"### {j['title']} — {j['company']}")
        a.write(f"{j.get('location') or 'Location not specified'} · {j.get('workplace_type') or 'work mode unknown'}")
        b.metric('Match',j.get('score',0))
        b.write(f"{j.get('verdict','—')} · {j.get('status','new')}")
        with c:
            url=j.get('apply_url') or j.get('url') or '#'
            st.link_button('Open job',url)
            if st.button('Workspace',key='ws_'+j['job_id']):
                try:
                    if base.strip():
                        st.session_state['workspace']=requests.get(f"{base.rstrip('/')}/workspace/{j['job_id']}",timeout=20).json()
                    else:
                        st.session_state['workspace']=build_workspace(j['job_id'])
                except Exception as e: st.error(str(e))

ws=st.session_state.get('workspace')
if ws:
    st.divider(); st.header(f"Application Workspace — {ws['job']['title']} @ {ws['job']['company']}")
    guard=ws['decision_guard']
    if not guard['consistent']:
        st.error(f"Decision inconsistency: score {guard['score']} expects {guard['expected']} but stored verdict is {guard['actual']}.")
    r=ws['recommendation']
    x,y,z=st.columns(3); x.metric('Application Quality',r['quality_score']); y.metric('Recommended',r['recommended_action']); z.metric('Match',guard['score'])
    t1,t2,t3=st.tabs(['Application','Recruiter','Interview'])
    with t1:
        st.json(ws['application'])
    with t2:
        st.json(ws['recruiter'])
    with t3:
        st.json(ws['interview'])
