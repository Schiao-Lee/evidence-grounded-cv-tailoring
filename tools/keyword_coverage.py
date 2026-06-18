#!/usr/bin/env python3
"""
keyword_coverage.py — JD keyword coverage check for a tailored CV PDF.

Used by Step 8 of prompts/tailor_per_job.md.

Usage:
    keyword_coverage.py <pdf> <keywords.txt>

Keywords file format:
    # must-have                 (lines starting with # are section markers)
    Power BI                    (one keyword/phrase per line)
    Python
    SQL
    # nice-to-have
    Snowflake
    Airflow

Rules:
- Sections from `# ...` markers; default section is "all" if no marker precedes a keyword.
- Blank lines ignored.
- Matching is case-insensitive, substring, on whitespace-squashed PDF text
  (so multi-word phrases that wrap across PDF lines still match).
- pdftotext must be on PATH.

Exit codes: 0 if anything ran, non-zero only on usage / missing-input / missing-pdftotext.
The script itself does NOT fail on low coverage — interpretation is up to the caller.
"""

import sys
import re
import shutil
import subprocess
from pathlib import Path
from collections import OrderedDict


def main() -> int:
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <pdf> <keywords.txt>", file=sys.stderr)
        return 64

    pdf, kw_file = Path(sys.argv[1]), Path(sys.argv[2])
    if not pdf.is_file():
        print(f"PDF not found: {pdf}", file=sys.stderr)
        return 66
    if not kw_file.is_file():
        print(f"Keywords file not found: {kw_file}", file=sys.stderr)
        return 66
    if not shutil.which("pdftotext"):
        print("pdftotext not installed (try: brew install poppler)", file=sys.stderr)
        return 69

    raw = subprocess.run(
        ["pdftotext", "-layout", "-nopgbrk", str(pdf), "-"],
        capture_output=True, text=True, check=True,
    ).stdout
    text = re.sub(r"\s+", " ", raw).lower()

    sections: "OrderedDict[str, dict]" = OrderedDict()
    current = "all"

    def ensure(sec: str) -> dict:
        return sections.setdefault(sec, {"total": 0, "present": [], "missing": []})

    for line in kw_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            current = line.lstrip("#").strip() or "all"
            ensure(current)
            continue
        sec = ensure(current)
        sec["total"] += 1
        if line.lower() in text:
            print(f"  PRESENT  [{current}]  {line}")
            sec["present"].append(line)
        else:
            print(f"  MISSING  [{current}]  {line}")
            sec["missing"].append(line)

    print()
    print("=" * 56)
    print("Coverage summary")
    print("=" * 56)
    for name, sec in sections.items():
        tot, pres = sec["total"], len(sec["present"])
        pct = (pres * 100 // tot) if tot else 0
        print(f"  {name:20s}  {pres:>3d} / {tot:<3d}  ({pct:>3d}%)")
        if sec["missing"]:
            print(f"    missing: {', '.join(sec['missing'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
