# Job Search Agent V6 — Recruiter + Interview Intelligence

V6 extends V5 into an end-to-end career copilot while preserving human control over applications.

## New
- Recruiter/contact CRM
- Personalized LinkedIn/email outreach drafts
- Outreach tracking and follow-up queue
- Interview plan generation per job
- Interview feedback analysis
- Outcome tracking: interview / offer / rejected
- Calibration report comparing job scores with actual outcomes
- V6 API namespace

## API
- `GET /v6/jobs/{job_id}/recruiter-brief`
- `POST /v6/contacts`
- `POST /v6/outreach`
- `GET /v6/jobs/{job_id}/interview-plan`
- `POST /v6/interviews`
- `POST /v6/outcomes`
- `GET /v6/followups`
- `GET /v6/outcomes/report`
- `GET /v6/outcomes/calibration`

## Safety / control
No LinkedIn credentials, CAPTCHA bypass, hidden endpoints, automatic connection requests, or automatic application submission.

## Run
```bash
pip install -r requirements.txt
uvicorn job_agent.api:app --reload
```
