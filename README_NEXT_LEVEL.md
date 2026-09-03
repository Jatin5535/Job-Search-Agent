# Job Search Agent — Next Level

## Run locally
```bash
cp .env.example .env
pip install -r requirements.txt
python -m job_agent.cli scan
streamlit run dashboard.py
```

Open the dashboard at http://localhost:8501 and API at http://localhost:8000/docs.

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
