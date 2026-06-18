#!/usr/bin/env python3
"""
redact_scan.py — scan a directory tree for personal data before publishing/sharing.

Catches the things you never want to push to a public repo: real email addresses,
phone numbers, absolute home paths, and key-like secrets. The synthetic examples/
folder is skipped by default (it is intentionally fake); pass --include-examples to
scan it too. Add your own name(s) with --deny to flag them as well.

Usage:
    redact_scan.py [DIR] [--deny "Jane Doe,jdoe"] [--include-examples]

Exit codes: 0 = clean, 1 = findings, 2 = bad usage.
"""

import argparse
import re
import sys
from pathlib import Path

SAFE_EMAIL_DOMAINS = ("example.com", "example.org", "example.net", "example", "test", "localhost")

PATTERNS = {
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "phone": re.compile(r"\+\d[\d\s\-().]{7,}\d|\b\d{3}[\s\-]\d{3}[\s\-]\d{3,4}\b"),
    "home_path": re.compile(r"/(?:Users|home)/[A-Za-z0-9._-]+/"),
    "secret": re.compile(
        r"sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|gh[pous]_[A-Za-z0-9]{20,}|"
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----"
    ),
}

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv"}
SKIP_SUFFIXES = {".pdf", ".png", ".jpg", ".jpeg", ".gif", ".aux", ".log", ".out",
                 ".pyc", ".docx", ".zip", ".DS_Store"}


def is_safe_email(match: str) -> bool:
    domain = match.rsplit("@", 1)[-1].lower()
    return any(domain == d or domain.endswith("." + d) for d in SAFE_EMAIL_DOMAINS)


def scan_file(path: Path, deny):
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    hits = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for kind, rx in PATTERNS.items():
            for m in rx.finditer(line):
                val = m.group(0)
                if kind == "email" and is_safe_email(val):
                    continue
                hits.append((kind, lineno, val.strip()))
        for term in deny:
            if term and term.lower() in line.lower():
                hits.append(("deny-term", lineno, term))
    return hits


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("dir", nargs="?", type=Path, default=Path(__file__).resolve().parent.parent)
    ap.add_argument("--deny", default="", help="comma-separated names/handles to flag")
    ap.add_argument("--include-examples", action="store_true",
                    help="also scan examples/ (skipped by default — it is synthetic)")
    args = ap.parse_args()

    root = args.dir.resolve()
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    deny = [t.strip() for t in args.deny.split(",") if t.strip()]

    total = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if not args.include_examples and (
            (rel.parts and rel.parts[0] == "examples") or ".example." in path.name
        ):
            continue
        if path.suffix.lower() in SKIP_SUFFIXES or path.name == ".DS_Store":
            continue
        for kind, lineno, val in scan_file(path, deny):
            print(f"  {kind:9}  {rel}:{lineno}  {val}")
            total += 1

    print("=" * 60)
    if total:
        print(f"  {total} potential finding(s) — review before publishing.")
        return 1
    print("  clean — no personal data found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
