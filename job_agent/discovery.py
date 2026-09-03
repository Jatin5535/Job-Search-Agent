from __future__ import annotations
import re, httpx
from urllib.parse import urlparse
from .collectors import clean_html
from .models import Job
HEADERS={'User-Agent':'PersonalJobSearchAgent/2.0'}

def discover_from_urls(urls:list[str]) -> list[Job]:
    """Fetch explicitly configured public career pages. No login, CAPTCHA or hidden API use."""
    out=[]
    for url in urls:
        try:
            r=httpx.get(url,headers=HEADERS,timeout=20,follow_redirects=True); r.raise_for_status()
            text=clean_html(r.text)
            host=urlparse(str(r.url)).netloc
            title=(re.search(r'<title[^>]*>(.*?)</title>',r.text,re.I|re.S) or [None,host])[1] or host
            # Discovery is intentionally conservative: it records the page as a review candidate rather than pretending it found individual jobs.
            out.append(Job(job_id=f'careerpage:{host}:{hash(str(r.url))}',source='career_page',company=host,title=title.strip(),location='',workplace_type='unspecified',url=str(r.url),apply_url=str(r.url),description=text[:12000],raw={'discovered_from':url}))
        except Exception:
            continue
    return out
