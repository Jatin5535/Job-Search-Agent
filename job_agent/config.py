from __future__ import annotations
import os
from pathlib import Path
import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def load_yaml(path: str):
    with open(ROOT / path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def profile():
    return load_yaml("config/profile.yaml").get("profile", {})


def sources():
    return load_yaml("config/sources.yaml").get("companies", []) or []


def database_url():
    return os.getenv("DATABASE_URL", "sqlite:///./jobs.db")


def min_score():
    return int(os.getenv("AGENT_MIN_SCORE", "80"))
