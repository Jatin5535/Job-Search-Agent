# Job Search Agent V7 — Apply Assistant

V7 adds a human-in-the-loop application layer for LinkedIn and Naukri links.

## Important platform boundary

LinkedIn currently states that it does not allow third-party software, browser extensions, bots, or other unauthorized automation that automates activity on LinkedIn. V7 therefore does **not** automate LinkedIn login, scraping, form completion, or Submit clicks.

For Naukri, V7 likewise uses a conservative assisted workflow unless an official API/partner integration explicitly authorizes automated application submission.

## What V7 does

- Detect LinkedIn / Naukri / other application URLs.
- Generate an application pack from the selected job and your profile.
- Prepare truthful reusable answers, application angle, resume emphasis, and cover-note content.
- Open the public application URL.
- Copy answers to clipboard via the local Apply Assistant page.
- Keep final review and Submit under your control.
- Mark the job as Applied after submission.

## API

`GET /apply/{job_id}/pack`

Returns the job, detected platform, application answers, application brief, and manual-submit checklist.

`POST /apply/{job_id}/mark-applied`

Marks the application as `applied`.

## Profile setup

Fill in the empty fields in `config/profile.yaml` for name, email, phone, LinkedIn, GitHub, portfolio, work authorization and notice period. Do not put passwords or session cookies in the file.
