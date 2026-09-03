# Job Search Agent V8 — Career Control Tower

V8 adds a unified application workspace and regression safety layer.

## New
- Decision-consistency guard between numeric score and stored verdict.
- Unified workspace API: `/workspace/{job_id}`.
- Single workspace containing recommendation, application pack, recruiter brief, and interview plan.
- Dashboard workspace view.
- Status update API under `/workspace/{job_id}/status`.
- Automated regression test for scoring + decision consistency.
- V8 API version/health reporting.

## Safety
V8 remains human-in-the-loop for LinkedIn/Naukri submission. It does not automate login, bypass controls, or click Submit on those platforms.

## Run
`pip install -r requirements.txt`
`uvicorn job_agent.api:app --reload --port 8000`
`streamlit run dashboard.py`
`pytest -q`
