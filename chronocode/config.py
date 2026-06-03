from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
DEFAULT_REPORT_DIR = ROOT_DIR / "reports"
DEFAULT_REPORT_DIR.mkdir(exist_ok=True)
