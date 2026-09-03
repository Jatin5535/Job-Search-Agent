from __future__ import annotations
from pathlib import Path
import re

DEFAULT_DIR=Path('data/resume')
DEFAULT_DIR.mkdir(parents=True, exist_ok=True)

def load_resume(path: str|None=None)->str:
    p=Path(path) if path else DEFAULT_DIR/'master_resume.txt'
    if not p.exists(): return ''
    return p.read_text(encoding='utf-8')

def extract_resume_skills(text:str, catalog:list[str])->list[str]:
    t=text.lower(); return [s for s in catalog if re.search(re.escape(s.lower()),t)]
