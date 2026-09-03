# Job Search Agent V8 — Career Control Tower + Broad Source Pack

V8 includes a broad, policy-conscious source layer for an India-first AI/GenAI job search.

## Sources

### Job-alert email sources
LinkedIn, Naukri, Indeed, Wellfound, Cutshort, Instahyre, Hirist, Foundit, Shine, TimesJobs, Glassdoor, FlexJobs.

### Public employer ATS
Greenhouse, Lever, Ashby, SmartRecruiters. Workable and other employers can use public career-page discovery where permitted.

### Remote/global candidates
Remote OK, We Work Remotely, Himalayas.

See `config/source_catalog.yaml` and `SOURCES.md`.

## Safe ingestion boundary
Do not automate authenticated browsing, credentialed scraping, CAPTCHA solving, hidden endpoints, or bulk application submission. Prefer official/public feeds, permitted public career pages, and job-alert emails.

## Run

```bash
pip install -r requirements.txt
python -m job_agent.cli scan
streamlit run dashboard.py
pytest -q
```
