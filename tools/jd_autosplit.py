#!/usr/bin/env python3
"""
jd_autosplit.py — fully automatic LinkedIn mega-dump splitter + cleaner.

Paste the raw LinkedIn job pages into JOB_APPLICATIONS/_intake/jds_<Date>
(noise and all), then run this. No manual cleaning, no audit file.

What it does:
1. Detects job boundaries: every LinkedIn job header has exactly one
   metadata line like "Cracow, ... · 17 hours ago · 15 applicants".
   Company = 2nd non-blank line above it, role = 1st non-blank line above it.
2. Cleans each job:
   - header keeps company / role / location-meta / workplace+employment type
   - the widget zone between the header and "About the job" is dropped
     (Apply/Saved/people cards/"Meet the hiring team"/etc.)
   - inside the body, known noise lines and trailing numeric id lines are dropped
3. Writes _jds_<Label>/NNN_Company_Role.txt, numbering continued from the
   highest NNN_ prefix across all existing _jds_*/ folders.
4. Seeds batch_runs/<date>_<label>_v1/jobs.csv with status=pending rows,
   ready for the batch driver prompt (prompts/batch_driver.md).

Usage:
    jd_autosplit.py <raw_intake_file> [--label jun13] [--dry-run]
                    [--job-apps DIR] [--start-id N]

Note: the noise/header heuristics are tuned for LinkedIn dumps. For other
sources, either adapt NOISE_EXACT / META_RE below, or just create the per-job
.txt files and a jobs.csv by hand — the batch driver only needs jobs.csv.
"""

import argparse
import csv
import datetime as dt
import re
import sys
from pathlib import Path

KIT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_JOB_APPS = KIT_ROOT / "JOB_APPLICATIONS"

META_RE = re.compile(r"\bago\b\s*·|·\s*\d+\s+applicants?\b")

# Lines worth keeping between the meta line and "About the job".
HEADER_KEEP_RE = re.compile(
    r"^(Hybrid|Remote|On-site|Full-time|Part-time|Internship|Contract|Temporary)\b", re.I
)

NOISE_EXACT = {
    "Apply", "Saved", "Save", "Show match details", "Tailor my resume",
    "Create cover letter", "Help me stand out", "People you can reach out to",
    "Show all", "Message", "Ask about job", "Meet the hiring team",
    "Show less", "Show more", "Easy Apply", "See how you compare to other applicants",
    "Promoted by hirer · Responses managed off LinkedIn",
    "Use AI to assess how you fit",
}

NOISE_RE = [
    re.compile(r"^•\s*\d+(st|nd|rd|th)$"),
    re.compile(r"^(Company|School) alumn?i? from ", re.I),
    re.compile(r"^Use AI to assess", re.I),
    re.compile(r"^Company logo for,", re.I),
    re.compile(r"^Promoted by hirer", re.I),
    re.compile(r"^\d{3,}$"),  # trailing numeric widget ids like "28924"
]


def is_noise(line):
    s = line.strip()
    if s in NOISE_EXACT:
        return True
    return any(rx.match(s) for rx in NOISE_RE)


def slugify(text):
    s = re.sub(r"[^0-9A-Za-z]+", "_", text).strip("_")
    return re.sub(r"_+", "_", s)


def find_jobs(lines):
    """Yield (company_idx, role_idx, meta_idx) for each job header."""
    jobs = []
    for i, line in enumerate(lines):
        if not META_RE.search(line):
            continue
        above = [j for j in range(i - 1, -1, -1) if lines[j].strip()][:2]
        if len(above) == 2:
            role_idx, company_idx = above[0], above[1]
            # guard against matching a meta-like line inside a JD body:
            # a real header's company/role lines are short title lines
            if len(lines[role_idx]) < 120 and len(lines[company_idx]) < 120:
                jobs.append((company_idx, role_idx, i))
    return jobs


def clean_job(lines, company_idx, role_idx, meta_idx, end_idx):
    company = lines[company_idx].strip()
    role = lines[role_idx].strip()
    out = [company, "", role, "", lines[meta_idx].strip()]

    # zone between meta line and "About the job": keep only type tags
    body_start = None
    zone_keep = []
    for j in range(meta_idx + 1, end_idx):
        if lines[j].strip() == "About the job":
            body_start = j
            break
        if HEADER_KEEP_RE.match(lines[j].strip()):
            zone_keep.append(lines[j].strip())
    if zone_keep:
        out += ["", " · ".join(dict.fromkeys(zone_keep))]

    out.append("")
    if body_start is None:
        body_start = meta_idx  # fallback: keep everything, noise-filtered
    blank = False
    for j in range(body_start, end_idx):
        line = lines[j].rstrip()
        if is_noise(line):
            continue
        if not line.strip():
            if not blank and len(out) > 7:
                out.append("")
            blank = True
            continue
        blank = False
        out.append(line)
    while out and not out[-1].strip():
        out.pop()
    return company, role, "\n".join(out) + "\n"


def next_job_id(job_apps, override):
    if override is not None:
        return override
    max_id = 0
    for f in job_apps.glob("_jds*/*.txt"):
        m = re.match(r"(\d+)_", f.name)
        if m:
            max_id = max(max_id, int(m.group(1)))
    return max_id + 1


JOBS_CSV_COLUMNS = [
    "id", "company", "role", "role_family", "page_mode", "jd_file", "status",
    "output_pdf", "must_have_cov", "gaps", "master_version", "page_count",
    "overfull_hboxes", "cxx_count", "fill_pct", "visual_qa", "tex_path",
    "report_path", "coverage_path",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raw", type=Path, help="raw intake file (e.g. _intake/jds_Jun13)")
    ap.add_argument("--label", default=None, help="batch label, default from filename")
    ap.add_argument("--job-apps", type=Path, default=DEFAULT_JOB_APPS)
    ap.add_argument("--start-id", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not args.raw.is_file():
        print(f"raw file not found: {args.raw}", file=sys.stderr)
        return 66
    label = args.label or args.raw.name.replace("jds_", "").lower()
    out_dir = args.job_apps / f"_jds_{label.capitalize()}"
    batch_dir = args.job_apps / "batch_runs" / f"{dt.date.today()}_{label}_v1"

    lines = args.raw.read_text(encoding="utf-8", errors="replace").splitlines()
    headers = find_jobs(lines)
    if not headers:
        print("no job headers detected — is this a LinkedIn dump?", file=sys.stderr)
        return 65

    job_id = next_job_id(args.job_apps, args.start_id)
    rows = []
    for n, (c_idx, r_idx, m_idx) in enumerate(headers):
        end_idx = headers[n + 1][0] if n + 1 < len(headers) else len(lines)
        company, role, text = clean_job(lines, c_idx, r_idx, m_idx, end_idx)
        fname = f"{job_id:03d}_{slugify(company)}_{slugify(role)}.txt"
        jd_path = out_dir / fname
        rows.append({
            "id": f"{job_id:03d}", "company": company, "role": role,
            "role_family": "", "page_mode": "one-page", "jd_file": str(jd_path),
            "status": "pending",
        })
        print(f"  {job_id:03d}  {company} — {role}  ({len(text.splitlines())} lines)")
        if not args.dry_run:
            out_dir.mkdir(parents=True, exist_ok=True)
            jd_path.write_text(text, encoding="utf-8")
        job_id += 1

    csv_path = batch_dir / "jobs.csv"
    if not args.dry_run:
        batch_dir.mkdir(parents=True, exist_ok=True)
        new = not csv_path.exists()
        with csv_path.open("a", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=JOBS_CSV_COLUMNS, restval="")
            if new:
                w.writeheader()
            w.writerows(rows)
    print(f"\n{len(rows)} job(s) -> {out_dir}/")
    print(f"jobs.csv -> {csv_path}{' (dry-run: not written)' if args.dry_run else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
