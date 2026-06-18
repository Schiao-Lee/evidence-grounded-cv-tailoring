#!/usr/bin/env python3
"""
build_jobs_master.py — aggregate every batch_runs/*/jobs.csv into one
cross-batch console: JOB_APPLICATIONS/jobs_master.csv.

The per-batch jobs.csv files stay authoritative for their run; this file is the
human-facing overview (sort, scan, find stale rows). Re-run after every batch.

Usage:
    build_jobs_master.py [--job-apps DIR] [--out PATH]

Staleness: rows whose master_version differs from the current git describe of the
kit root are marked stale_candidate=yes — review before regenerating. (If the kit
is not a git repo, master_version staleness is simply not flagged.)
"""

import argparse
import csv
import subprocess
import sys
from pathlib import Path

KIT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_JOB_APPS = KIT_ROOT / "JOB_APPLICATIONS"

CORE_COLUMNS = [
    "batch_id", "id", "company", "role", "role_family", "page_mode",
    "jd_file", "status", "output_pdf", "must_have_cov", "gaps",
    "master_version", "stale_candidate",
]


def current_master_version():
    """Base tag of HEAD (e.g. 'master-2026.05'); '' if not a git repo / no tags."""
    out = subprocess.run(
        ["git", "-C", str(KIT_ROOT), "describe", "--tags", "--abbrev=0"],
        capture_output=True, text=True,
    )
    return out.stdout.strip() if out.returncode == 0 else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job-apps", type=Path, default=DEFAULT_JOB_APPS)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    batch_dir = args.job_apps / "batch_runs"
    out_path = args.out or (args.job_apps / "jobs_master.csv")
    csv_files = sorted(batch_dir.glob("*/jobs.csv"))
    if not csv_files:
        print(f"No jobs.csv found under {batch_dir}", file=sys.stderr)
        return 1

    head = current_master_version()
    rows, extra_cols = [], []
    for f in csv_files:
        batch_id = f.parent.name
        with f.open(newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                row = {k: (v or "").strip() for k, v in row.items() if k}
                row["batch_id"] = batch_id
                mv = row.get("master_version", "")
                row["stale_candidate"] = "yes" if head and mv and head not in mv else ""
                rows.append(row)
                for k in row:
                    if k not in CORE_COLUMNS and k not in extra_cols:
                        extra_cols.append(k)

    columns = CORE_COLUMNS + extra_cols
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    stale = sum(1 for r in rows if r["stale_candidate"] == "yes")
    print(f"{out_path}: {len(rows)} rows from {len(csv_files)} batches "
          f"(current master: {head or 'unknown'}; stale candidates: {stale})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
