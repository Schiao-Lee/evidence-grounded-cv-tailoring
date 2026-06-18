#!/usr/bin/env python3
"""
check_phone_prep.py — report generated-CV rows that have no phone-interview prep file.

Phone-interview prep lives in the TOP-LEVEL PHONE_INTERVIEW_PREP/ folder. Every
generated CV should have exactly one prep .md keyed by the same jobs_master row id.

"Generated" is detected from DISK, not the jobs_master status column (that console
goes stale). A row counts as generated when its job folder contains a CV_*.pdf. The
folder is found from the jd_file column (strip the leading "<id>_" and the extension
-> folder name), with the output_pdf path as a fallback.

Usage:
    check_phone_prep.py [--master CSV] [--prep DIR] [--row N] [--min-row N]

Exit codes:
    0 = every generated row is covered (or the single --row N is covered)
    1 = at least one generated row (or --row N) has no prep file
    2 = usage / missing input error
"""

import argparse
import csv
import re
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
WORKSPACE = TOOLS_DIR.parent  # kit root
DEFAULT_MASTER = WORKSPACE / "JOB_APPLICATIONS" / "jobs_master.csv"
DEFAULT_PREP = WORKSPACE / "PHONE_INTERVIEW_PREP"
JOB_APPS = WORKSPACE / "JOB_APPLICATIONS"


def covered_row_ids(prep_dir):
    """Integer row ids that already have a prep file (top-level + subfolders)."""
    ids = set()
    if not prep_dir.is_dir():
        return ids
    for p in prep_dir.rglob("*.md"):
        m = re.match(r"(\d+)_", p.name)
        if m:
            ids.add(int(m.group(1)))
    return ids


def folder_for_row(row):
    """Best-effort job folder name for a jobs_master row, via jd_file then output_pdf."""
    jd = (row.get("jd_file") or "").strip()
    if jd:
        slug = re.sub(r"^\d+_", "", Path(jd).stem)
        if (JOB_APPS / slug).is_dir():
            return slug
    pdf = (row.get("output_pdf") or "").strip()
    if pdf:
        parent = Path(pdf).parent.name
        if (JOB_APPS / parent).is_dir():
            return parent
    return None


def is_generated(folder):
    return bool(folder) and any((JOB_APPS / folder).glob("CV_*.pdf"))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--master", type=Path, default=DEFAULT_MASTER)
    ap.add_argument("--prep", type=Path, default=DEFAULT_PREP)
    ap.add_argument("--row", type=int, default=None, help="check a single row id and exit")
    ap.add_argument("--min-row", type=int, default=None, help="ignore rows below this id")
    args = ap.parse_args()

    if not args.master.is_file():
        print(f"jobs_master not found: {args.master}", file=sys.stderr)
        return 2
    if not args.prep.is_dir():
        print(f"prep folder not found: {args.prep}", file=sys.stderr)
        return 2

    covered = covered_row_ids(args.prep)

    generated = []      # (id, company, role, folder)
    stale_console = []  # generated on disk but csv still says pending
    with args.master.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                rid = int(row["id"])
            except (KeyError, ValueError, TypeError):
                continue
            if args.min_row is not None and rid < args.min_row:
                continue
            folder = folder_for_row(row)
            if not is_generated(folder):
                continue
            generated.append((rid, (row.get("company") or "").strip(),
                              (row.get("role") or "").strip(), folder))
            if (row.get("status") or "").strip().lower() in ("", "pending"):
                stale_console.append(rid)

    if args.row is not None:
        ok = args.row in covered
        gen_ids = {g[0] for g in generated}
        where = "covered" if ok else "MISSING"
        extra = "" if args.row in gen_ids else " (note: not detected as generated)"
        print(f"row {args.row}: phone prep {where}{extra}")
        return 0 if ok else 1

    missing = [g for g in generated if g[0] not in covered]
    print(f"\nPhone-interview prep coverage — {args.prep}")
    print("=" * 70)
    print(f"  generated CVs: {len(generated)}   covered: {len(generated) - len(missing)}   "
          f"missing: {len(missing)}")
    if missing:
        print("\n  Rows generated but with NO phone prep:")
        for rid, company, role, folder in sorted(missing):
            print(f"    row {rid:>3}  {company} — {role}")
            print(f"             ({folder})")
    if stale_console:
        print(f"\n  (note) jobs_master still marks these generated rows pending — "
              f"rerun build_jobs_master.py: {sorted(stale_console)}")
    print("=" * 70)
    print("  Overall: " + ("FAIL — create the missing prep files" if missing else "PASS"))
    print()
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
