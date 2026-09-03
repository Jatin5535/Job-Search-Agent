# Job Search Agent V5 — Recruiter & Application Copilot

V5 upgrades the Career Control Tower with a human-in-the-loop application copilot.

## Added
- Per-job application brief
- Resume emphasis suggestions
- Gap / claim-verification checklist
- Draft cover note
- Interview question prompts
- Public company research URL generation
- Application quality score separate from raw job-match score
- Streamlit control-tower dashboard integration
- New API: `GET /copilot/job/{job_id}`

## Safety boundary
The system prepares and ranks applications but does **not** submit applications automatically. It does not require LinkedIn credentials or automate authenticated activity.

## Run
```bash
pip install -r requirements.txt
python -m job_agent.cli init
uvicorn job_agent.api:app --reload --port 8000
streamlit run dashboard.py
```

## Workflow
1. Scan public job sources and configured alert inbox.
2. Normalize and score jobs.
3. Open a shortlisted job in the dashboard.
4. Generate the application brief.
5. Review the resume/cover note and verify every claim.
6. Apply manually.
7. Update the application status so the learning loop gets better over time.
