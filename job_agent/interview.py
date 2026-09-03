from __future__ import annotations
from typing import Any
import re


def analyze_feedback(text: str) -> dict[str, Any]:
    t = (text or '').lower()
    strengths = []
    gaps = []
    for key, words in {
        'communication': ('communication', 'explained clearly', 'clarity'),
        'python': ('python',),
        'aws': ('aws', 'cloud'),
        'llm/rag': ('llm', 'rag', 'retrieval'),
        'system design': ('system design', 'architecture', 'architect'),
        'leadership': ('leadership', 'led', 'stakeholder'),
        'problem solving': ('problem solving', 'reasoning', 'approach'),
    }.items():
        if any(w in t for w in words):
            strengths.append(key)
    for key, words in {
        'depth': ('not deep', 'too shallow', 'depth'),
        'algorithms': ('algorithm', 'dsa', 'coding round'),
        'system design': ('system design', 'architecture gap'),
        'cloud depth': ('aws', 'azure', 'gcp'),
        'communication': ('communication gap', 'unclear', 'rambling'),
    }.items():
        if any(w in t for w in words) and key not in strengths:
            gaps.append(key)
    sentiment = 'positive' if any(w in t for w in ('strong', 'great', 'good', 'positive', 'impressed')) else 'mixed'
    return {'sentiment': sentiment, 'strengths': strengths[:8], 'gaps': gaps[:8]}


def interview_plan(job: dict[str, Any]) -> dict[str, Any]:
    matched = job.get('matched') or []
    title = job.get('title', 'role')
    qs = []
    for skill in matched[:6]:
        qs.append(f"Prepare one concrete production example for {skill}: problem, design, trade-offs, scale and result.")
    qs += [
        f"Give a 90-second explanation of why your background fits {title}.",
        "Be ready to whiteboard an end-to-end AI system and explain reliability, security, cost and observability trade-offs.",
        "Prepare a failure story: what broke, how you diagnosed it, and what you changed afterward.",
    ]
    return {'title': title, 'questions': qs[:10], 'focus_areas': matched[:8]}
