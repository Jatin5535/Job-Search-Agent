from __future__ import annotations
import re
from datetime import datetime, timezone


def tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9+.#/-]{2,}", (text or "").lower()))


def contains_phrase(text: str, phrase: str) -> bool:
    return phrase.lower() in (text or "").lower()


def score_job(job, p: dict):
    title = (job.title or "").lower()
    body = f"{job.title} {job.description} {job.department or ''} {job.location} {job.workplace_type}".lower()
    score = 0
    reasons = []

    # Title fit: 0-20
    target_titles = p.get("target_titles", [])
    exact_hits = sum(1 for t in target_titles if t.lower() in title)
    title_points = min(20, 8 + exact_hits * 6) if exact_hits else 0
    score += title_points
    if title_points:
        reasons.append(f"Strong target-title match (+{title_points})")

    # Hard must-have skills: 0-30
    must = p.get("must_have_skills", [])
    must_hits = [s for s in must if contains_phrase(body, s)]
    must_points = round(30 * len(must_hits) / max(1, len(must)))
    score += must_points
    if must_hits:
        reasons.append(f"Must-have skills: {', '.join(must_hits)} (+{must_points})")

    # Strong skills: 0-15
    strong = p.get("strong_skills", [])
    strong_hits = [s for s in strong if contains_phrase(body, s)]
    strong_points = round(15 * min(len(strong_hits), 8) / 8)
    score += strong_points
    if strong_hits:
        reasons.append(f"Strong skills: {', '.join(strong_hits[:6])} (+{strong_points})")

    # Experience fit: 0-10
    years = p.get("years_experience", 2)
    senior_words = ["senior", "staff", "principal", "director", "head"]
    if any(w in title for w in senior_words):
        score -= 10
        reasons.append("Seniority looks above target (-10)")
    elif re.search(r"\b0\s*(?:-|to)\s*3\s+years?\b|\b1\s*(?:-|to)\s*3\s+years?\b", body):
        score += 10
        reasons.append("Experience range looks aligned (+10)")
    elif re.search(r"\b(?:2|3)\+?\s+years?\b", body):
        score += 8
        reasons.append("Experience requirement looks close (+8)")
    elif re.search(r"\b[5-9]\+?\s+years?\b|\b10\+\s+years?\b", body):
        score -= 8
        reasons.append("Experience requirement looks high (-8)")
    else:
        score += 5

    # Location/work mode: 0-10
    loc = (job.location or "").lower()
    remote = (job.workplace_type or "").lower() == "remote" or "remote" in loc or "remote" in body
    india = any(x.lower() in loc for x in p.get("location_preferences", {}).get("india_cities", []))
    international = any(x.lower() in loc for x in p.get("location_preferences", {}).get("international", []))
    if remote and p.get("location_preferences", {}).get("remote_india", True):
        score += 10; reasons.append("Remote-friendly (+10)")
    elif india or international:
        score += 8; reasons.append("Target geography (+8)")
    else:
        score += 2

    # Cloud/architecture relevance: 0-10
    cloud_terms = ["aws", "azure", "gcp", "cloud", "architecture", "architect"]
    cloud_hits = [x for x in cloud_terms if x in body]
    cloud_points = min(10, len(set(cloud_hits)) * 2)
    score += cloud_points
    if cloud_points:
        reasons.append(f"Cloud/architecture relevance (+{cloud_points})")

    # Freshness: 0-5. We reward recent ISO/timestamp fields when parseable.
    freshness = 3
    try:
        if job.posted_at:
            if str(job.posted_at).isdigit():
                posted = datetime.fromtimestamp(int(job.posted_at) / 1000, tz=timezone.utc)
            else:
                posted = datetime.fromisoformat(str(job.posted_at).replace("Z", "+00:00"))
            age_days = max(0, (datetime.now(timezone.utc) - posted).days)
            freshness = 5 if age_days <= 3 else 4 if age_days <= 7 else 2 if age_days <= 30 else 0
    except Exception:
        pass
    score += freshness
    if freshness:
        reasons.append(f"Freshness (+{freshness})")

    # Penalize obvious mismatch/low-signal title terms.
    negatives = p.get("avoid_title_terms", [])
    neg_hits = [n for n in negatives if n.lower() in title]
    if neg_hits:
        score -= min(15, 5 * len(neg_hits))
        reasons.append(f"Avoid-title terms: {', '.join(neg_hits)}")

    score = max(0, min(100, int(score)))
    return score, reasons
