from __future__ import annotations
from typing import Any
import re, urllib.parse


def company_query(company: str, extra='careers linkedin funding layoffs') -> str:
    return 'https://www.google.com/search?q=' + urllib.parse.quote_plus(f'{company} {extra}')

def public_signals(job: dict[str,Any]) -> dict[str,Any]:
    company=job.get('company','')
    desc=(job.get('description','') or '').lower()
    signals=[]
    if any(x in desc for x in ('customer-facing','client-facing','enterprise')): signals.append('enterprise/customer exposure')
    if any(x in desc for x in ('production','scale','high availability','reliability')): signals.append('production/scale signal')
    if any(x in desc for x in ('visa sponsorship','relocation assistance')): signals.append('mobility/support signal')
    if any(x in desc for x in ('security clearance','us citizenship required')): signals.append('eligibility restriction')
    return {'company':company,'signals':signals,'research_url':company_query(company) if company else None}
