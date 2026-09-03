# Job Search Agent V3 — Career Control Tower

This version upgrades the original agent with a richer scoring layer, email-alert ingestion, local-LLM analysis hooks, resume storage, status pipeline, and a control-tower dashboard.

## Start

```bash
python -m job_agent.cli scan
streamlit run dashboard.py
```

## Email alerts

Create forwarding/alerts according to the policies of the job site. The agent can ingest job-alert messages through IMAP when `IMAP_USER` and `IMAP_PASSWORD` are configured.

## Local AI

Set `LLM_ENABLED=true` and run Ollama separately. The deterministic scorer is still the fallback.

## Resume

Put your truth-checked master resume in `data/resume/master_resume.txt`. Resume tailoring remains an assistive workflow; review every change before submission.

## Guardrails

No login automation, CAPTCHA solving, credential harvesting, or bulk application submission. Use official feeds/APIs, permitted employer career pages, and job-alert emails.
