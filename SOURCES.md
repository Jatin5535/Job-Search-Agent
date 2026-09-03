# Source Strategy

This agent uses three classes of sources:

1. **Job-alert email sources** — LinkedIn, Naukri, Indeed, Wellfound, Cutshort, Instahyre, Hirist, Foundit, Shine, TimesJobs, Glassdoor, and FlexJobs. Configure alerts on the services themselves and let the agent ingest the resulting emails through your mailbox. This avoids credentialed scraping.

2. **Public employer ATS sources** — Greenhouse, Lever, Ashby, and SmartRecruiters are supported as explicit employer-board configurations. Workable and other employers can be added through public career-page URLs where permitted.

3. **Public remote/job sites** — Remote OK, We Work Remotely, and Himalayas are kept as public-source candidates; add a permitted feed or public page when available.

The catalog is intentionally source-complete rather than pretending that every site has a public API. Where a service does not expose an authorized public API/feed, use its alert email or public employer career page instead.
