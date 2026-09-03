from __future__ import annotations
from typing import Any
import re


def _clean(s: str) -> str:
    return re.sub(r'\s+', ' ', (s or '').strip())


def recruiter_brief(job: dict[str, Any], profile: dict[str, Any], contact: dict[str, Any] | None = None) -> dict[str, Any]:
    company = job.get('company', 'the company')
    title = job.get('title', 'this role')
    matched = job.get('matched') or []
    focus = ', '.join(matched[:4]) or 'AI engineering and cloud architecture'
    name = (contact or {}).get('name') or 'there'
    role_hook = f"the {title} opportunity at {company}"
    message = (
        f"Hi {name}, I came across {role_hook} and it stood out because of the work around {focus}. "
        "My background is in AI engineering, GenAI/LLMs, RAG and cloud solutioning, and I’m exploring roles where I can stay hands-on while owning production outcomes. "
        "I’d be glad to connect and share a concise profile if the role is still active."
    )
    email = (
        f"Subject: {title} — quick introduction\n\n"
        f"Hi {name},\n\nI’m reaching out regarding the {title} role at {company}. "
        f"The position aligns with my experience in {focus}, along with AI solution architecture and cloud delivery. "
        "I’m especially interested in opportunities where I can contribute hands-on to production AI systems.\n\n"
        "Happy to share a focused resume or speak briefly if helpful.\n\nBest,\nCandidate"
    )
    return {
        'company': company,
        'title': title,
        'contact': contact or {},
        'linkedin_message': _clean(message),
        'email': email,
        'personalization_points': matched[:6],
        'do_not_claim': [x for x in (profile.get('must_have_skills') or []) if x not in matched][:5],
        'follow_up_days': [3, 7, 14],
    }


def follow_up_message(company: str, title: str, stage: str, contact_name: str = 'there') -> str:
    if stage == 'applied':
        return f"Hi {contact_name}, just following up on my application for the {title} role at {company}. I’m still very interested and happy to share any additional information that would help."
    if stage == 'screening':
        return f"Hi {contact_name}, thanks again for the conversation about {title}. I enjoyed learning more about the role and remain very interested. Happy to provide anything needed for the next step."
    return f"Hi {contact_name}, I wanted to follow up regarding {title} at {company}. I’m still interested and would be glad to continue the conversation when convenient."
