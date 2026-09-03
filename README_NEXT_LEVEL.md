# Job Search Agent — Next Level

## Run locally
```bash
cp .env.example .env
pip install -r requirements.txt
python -m job_agent.cli scan
streamlit run dashboard.py
```

Open the dashboard at http://localhost:8501 and API at http://localhost:8000/docs.

## Connect Naukri job alerts
1. In Naukri, create or enable job alerts matching your profile and deliver them to the mailbox used below.
2. Copy `.env.example` to `.env` and set `IMAP_HOST`, `IMAP_USER`, and `IMAP_PASSWORD` (use a Gmail app password when applicable).
3. Set `IMAP_FROM=naukri.com` to ingest only Naukri alert mail.
4. Run **Run public job scan** in the dashboard, or call `POST /run`.

The connector reads permitted alert emails only. It does not log in to Naukri, scrape pages, bypass CAPTCHA, or submit applications.

## Optional local AI
Install Ollama separately, then pull a model such as `qwen2.5:7b`. The deterministic scorer remains the fallback, so the system does not require a paid API.

## Recommended production flow
1. Scheduled source collection.
2. Normalize + deduplicate.
3. Deterministic hard filters.
4. Local LLM semantic score for borderline/high-value jobs.
5. Dashboard review queue.
6. Human approval.
7. Resume tailoring.
8. Manual application.
9. Status tracking + interview follow-up.

Do not automate login, CAPTCHA solving, or bulk application submission. Use official feeds/APIs, job-alert emails, or public employer career pages where permitted.
