from __future__ import annotations
import re
import httpx
from .models import Job

TIMEOUT = httpx.Timeout(30.0)
HEADERS = {"User-Agent": "PersonalJobSearchAgent/1.0 (+local-user-agent)"}


def clean_html(text: str) -> str:
    text = re.sub(r"<script[\s\S]*?</script>", " ", text or '', flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text or '', flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def fetch_json(url: str):
    with httpx.Client(timeout=TIMEOUT, headers=HEADERS, follow_redirects=True) as client:
        r = client.get(url)
        r.raise_for_status()
        return r.json()


def greenhouse(company: dict) -> list[Job]:
    token = company["board_token"]
    data = fetch_json(f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true")
    jobs = []
    for x in data.get("jobs", []):
        loc = (x.get("location") or {}).get("name", "")
        desc = clean_html(x.get("content", ""))
        jobs.append(Job(
            job_id=f"greenhouse:{token}:{x.get('id')}",
            source="greenhouse", company=company["name"], title=x.get("title", ""),
            location=loc, workplace_type="unspecified", url=x.get("absolute_url", ""),
            apply_url=x.get("absolute_url", ""), description=desc,
            posted_at=x.get("updated_at") or x.get("created_at"),
            department=((x.get("departments") or [{}])[0].get("name") if x.get("departments") else None), raw=x
        ))
    return jobs


def lever(company: dict) -> list[Job]:
    account = company["account"]
    data = fetch_json(f"https://api.lever.co/v0/postings/{account}?mode=json")
    # Lever's public postings API may expose either a list or an object depending on endpoint/version.
    items = data.get("data", data) if isinstance(data, dict) else data
    if isinstance(items, dict):
        items = [items]
    jobs = []
    for x in items or []:
        content = x.get("content") or {}
        cats = x.get("categories") or {}
        desc = content.get("description") or x.get("description") or ""
        urls = x.get("urls") or {}
        jobs.append(Job(
            job_id=f"lever:{account}:{x.get('id')}",
            source="lever", company=company["name"], title=x.get("text", ""),
            location=cats.get("location", ""), workplace_type=x.get("workplaceType", "unspecified"),
            url=urls.get("show", ""), apply_url=urls.get("apply", ""), description=clean_html(desc),
            posted_at=(str(x.get("createdAt")) if x.get("createdAt") else None),
            salary=x.get("salaryDescription"), department=cats.get("department"), raw=x
        ))
    return jobs



def ashby(company: dict) -> list[Job]:
    board = company["job_board_name"]
    data = fetch_json(f"https://api.ashbyhq.com/posting-api/job-board/{board}?includeCompensation=true")
    jobs=[]
    for x in data.get('jobs', []):
        if x.get('isListed') is False: continue
        locs=[x.get('location','')] + [z.get('location','') for z in (x.get('secondaryLocations') or [])]
        loc=', '.join([z for z in locs if z])
        desc=x.get('descriptionPlain') or x.get('descriptionHtml') or ''
        comp=x.get('compensation') or {}
        salary=comp.get('text') if isinstance(comp,dict) else str(comp) if comp else None
        jobs.append(Job(
            job_id=f"ashby:{board}:{x.get('jobUrl') or x.get('applyUrl') or x.get('title')}",
            source='ashby', company=company['name'], title=x.get('title',''), location=loc,
            workplace_type=x.get('workplaceType','unspecified'), url=x.get('jobUrl',''),
            apply_url=x.get('applyUrl') or x.get('jobUrl',''), description=clean_html(desc),
            posted_at=x.get('publishedDate'), salary=salary, department=x.get('department'), raw=x))
    return jobs


def smartrecruiters(company: dict) -> list[Job]:
    ident=company['company_identifier']
    base=f"https://api.smartrecruiters.com/v1/companies/{ident}/postings"
    data=fetch_json(base + '?limit=100')
    jobs=[]
    for x in data.get('content', data.get('jobs', [])):
        loc=x.get('location') or {}
        if isinstance(loc,dict):
            location=', '.join([str(loc.get(k,'')) for k in ('city','region','country') if loc.get(k)])
        else: location=str(loc)
        pid=x.get('id') or x.get('uuid')
        url=x.get('ref') or x.get('jobAdUrl') or f"https://careers.smartrecruiters.com/{ident}/{pid}"
        jobs.append(Job(job_id=f"smartrecruiters:{ident}:{pid}", source='smartrecruiters', company=company['name'],
                        title=x.get('name') or x.get('title',''), location=location, workplace_type='unspecified',
                        url=url, apply_url=x.get('applyUrl') or url, description=clean_html(x.get('jobAd','') if isinstance(x.get('jobAd'),str) else ''),
                        posted_at=x.get('releasedDate') or x.get('postedDate'), salary=None, department=None, raw=x))
    return jobs

def collect_all(sources: list[dict]) -> list[Job]:
    out = []
    errors = []
    for source in sources:
        try:
            provider = source["provider"].lower()
            if provider == "greenhouse":
                out.extend(greenhouse(source))
            elif provider == "lever":
                out.extend(lever(source))
            elif provider == "ashby":
                out.extend(ashby(source))
            elif provider == "smartrecruiters":
                out.extend(smartrecruiters(source))
            else:
                errors.append(f"Unsupported provider: {provider}")
        except Exception as exc:
            errors.append(f"{source.get('name','unknown')}: {exc}")
    return out, errors
