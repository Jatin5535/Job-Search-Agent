# Job Search Agent V4 — Career Control Tower + Learning Loop

V4 adds four major capabilities over V3: explicit user feedback learning, bounded company-history signals, configurable public career-page discovery, and optional semantic scoring with local Ollama. It remains human-approved for applications.

## Run

```bash
python -m job_agent.cli scan
streamlit run dashboard.py
```

## Configure

1. Edit `config/profile.yaml`.
2. Add public Greenhouse/Lever boards in `config/sources.yaml`.
3. Optionally add permitted public employer career-page URLs under `career_pages`.
4. Set `llm_enabled: true` only when Ollama is available locally.

## Learning loop

The dashboard has Like / Skip actions. You can also use:

```bash
python -m job_agent.cli feedback JOB_ID shortlist 1
python -m job_agent.cli feedback JOB_ID reject -1
python -m job_agent.cli feedback-summary
```

The learning signal is deliberately bounded to ±8 points so a handful of clicks cannot completely override the candidate profile.

## Safety / platform boundaries

No credentialed scraping, CAPTCHA solving, session-token use, stealth browser automation, or bulk application submission. Use employer-published pages, official feeds/APIs, and job-alert emails you are allowed to access. Treat auto-generated resume changes as drafts requiring review.

## Architecture

```text
Public job feeds / permitted career pages / alerts
                  ↓
              Ingestion
                  ↓
         Normalize + dedupe
                  ↓
      Rule score + semantic score
                  ↓
       Preference learning loop
                  ↓
        Opportunity ranking
          ↙         ↓        ↘
      APPLY      REVIEW      SKIP
         ↓          ↓
      Tracker   Human review
         └──────────┘
             ↓
         Feedback
             ↓
      Better ranking next run
```
