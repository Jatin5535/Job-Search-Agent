import yaml
from pathlib import Path

EXPECTED_EMAIL_SOURCES = {
    "linkedin", "naukri", "indeed", "wellfound", "cutshort", "instahyre",
    "hirist", "foundit", "shine", "timesjobs", "glassdoor", "flexjobs"
}

def test_source_catalog_and_config():
    root = Path(__file__).resolve().parents[1]
    cfg = yaml.safe_load((root / "config/sources.yaml").read_text())
    catalog = yaml.safe_load((root / "config/source_catalog.yaml").read_text())
    assert EXPECTED_EMAIL_SOURCES.issubset(set(cfg["email_alert_sources"]))
    names = {x["site"] for x in catalog["job_boards_via_alert_email"]}
    assert EXPECTED_EMAIL_SOURCES.issubset(names)
    providers = {x.get("provider") for x in catalog["public_ats"]}
    assert {"greenhouse", "lever", "ashby", "smartrecruiters"}.issubset(providers)
