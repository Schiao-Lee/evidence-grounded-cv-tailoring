#!/usr/bin/env python3
"""
qa_one_job.py — deterministic QA gate for one tailored CV job folder.

Replaces "LLM self-discipline" with machine checks for the failure modes that
recur in AI tailoring runs (format drift, dropped language row, confessional
wording, invented metrics, stale artifacts).

PERSONAL FACTS ARE NOT HARDCODED HERE. The contact / education / language
checks are built from your profile.yaml via profile_loader.py. Edit profile.yaml,
never this file, to make the gate enforce your own facts.

Usage:
    qa_one_job.py <job_folder> [options]

Options:
    --pages N             expected page count (default 1)
    --max-bottom-ws PT    fail if bottom whitespace exceeds this (profile default)
    --min-bottom-ws PT    fail if bottom whitespace is below this (default 20.0)
    --max-right-ws PT     right-margin whitespace ceiling (profile default)
    --allow-cpp           do not fail on standalone "C++" in the PDF text
    --json PATH           also write gate results as JSON (default <base>_qa.json;
                          pass "-" to skip writing)
    --profile PATH        profile.yaml (default: auto-discovered from kit root)
    --master PATH         master CV .tex     (default: from profile paths)
    --bank PATH           project bank .md   (default: from profile paths)
    --evidence PATH       evidence map .md   (default: from profile paths)
    --forbidden PATH      forbidden phrase list (default: tools/qa_forbidden_phrases.txt)

Gates (FAIL blocks completion; WARN must be acknowledged in the _REPORT.md):
    files          .tex / .pdf / _REPORT.md / keywords / decision_trace.json present
    pages          page count == --pages
    overfull       zero "Overfull \\hbox" in the .log
    cpp            zero standalone "C++" in PDF text (unless --allow-cpp)
    languages      every language+level pair from profile.yaml present in PDF text
    contact        phone AND email from profile.yaml present in PDF text
                   (catches a header collapsed to the links-only line)
    education      institution + degree from profile.yaml present in PDF; WARN if
                   the .tex Education is freeform instead of the \\entry macro
    forbidden      no forbidden phrase / excluded language appears in PDF text
    bottom_ws      bottom whitespace within bounds (dense max 120pt / balanced 150pt)
    right_ws       right-margin whitespace not bloated
    numeric_subset every numeric claim token in the .tex body exists in
                   master / project bank / evidence map (anti-hallucination)
    staleness      *_text_extract.txt / *_coverage.txt / visual_qa png not older
                   than the PDF (WARN — re-extract before quoting)
    coverage       keyword_coverage.py summary reported (INFO)

Exit codes: 0 = all gates pass (warnings allowed), 1 = at least one FAIL,
            2+ = usage / missing input errors.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS_DIR))
import profile_loader as pl  # noqa: E402

DEFAULT_FORBIDDEN = TOOLS_DIR / "qa_forbidden_phrases.txt"

# Layout lengths that are not content claims (used by the numeric subset gate).
LENGTH_RE = re.compile(r"-?\d+(?:\.\d+)?\s*(?:pt|em|ex|cm|mm|in|bp|sp|fil{1,3})\b")


class Gate:
    def __init__(self, name):
        self.name = name
        self.status = "PASS"
        self.notes = []

    def fail(self, msg):
        self.status = "FAIL"
        self.notes.append(msg)

    def warn(self, msg):
        if self.status == "PASS":
            self.status = "WARN"
        self.notes.append(msg)

    def info(self, msg):
        self.notes.append(msg)


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def pdf_text(pdf):
    out = run(["pdftotext", "-layout", "-nopgbrk", str(pdf), "-"])
    if out.returncode != 0:
        return None
    return out.stdout


def pdf_page_count(pdf):
    out = run(["pdfinfo", str(pdf)])
    m = re.search(r"^Pages:\s+(\d+)", out.stdout, re.M)
    return int(m.group(1)) if m else None


def pdf_margins(pdf):
    """Page-1 whitespace in points via pdftotext -bbox word boxes."""
    out = run(["pdftotext", "-bbox", "-l", "1", str(pdf), "-"])
    if out.returncode != 0:
        return None
    xml_text = re.sub(r'xmlns="[^"]+"', "", out.stdout, count=1)
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return None
    page = root.find(".//page")
    if page is None:
        return None
    width = float(page.get("width"))
    height = float(page.get("height"))
    words = page.findall(".//word")
    if not words:
        return None
    xmaxes = [float(w.get("xMax")) for w in words]
    xmins = [float(w.get("xMin")) for w in words]
    ymaxes = [float(w.get("yMax")) for w in words]
    return {
        "left": min(xmins),
        "right": width - max(xmaxes),
        "bottom": height - max(ymaxes),
    }


def detect_profile(tex_source):
    """Return 'dense' | 'balanced' from the CVStyleProfile in the .tex, default dense."""
    m = re.search(r"\\CVStyleProfile\}?\{(dense|balanced)\}", tex_source)
    if not m:
        m = re.search(r"CVStyleProfile.*?(balanced|dense)", tex_source)
    return m.group(1) if m else "dense"


def tex_body(tex_source):
    body = tex_source.split(r"\begin{document}", 1)[-1]
    body = re.sub(r"(?<!\\)%.*", "", body)
    body = body.replace(r"\%", "%")
    body = LENGTH_RE.sub(" ", body)
    return body


def numeric_tokens(text):
    text = text.replace(",", "")
    tokens = set()
    for m in re.finditer(r"\d+(?:\.\d+)?%?", text):
        tok = m.group(0)
        if len(tok.rstrip("%").replace(".", "")) < 2 and not tok.endswith("%"):
            continue
        tokens.add(tok.rstrip("."))
    return tokens


def discover(folder):
    pdfs = sorted(folder.glob("CV_*.pdf"), key=lambda p: p.stat().st_mtime)
    if not pdfs:
        pdfs = sorted(folder.glob("*.pdf"), key=lambda p: p.stat().st_mtime)
    if not pdfs:
        return None
    pdf = pdfs[-1]
    base = pdf.with_suffix("")
    return {
        "pdf": pdf,
        "tex": base.with_suffix(".tex"),
        "log": base.with_suffix(".log"),
        "report": Path(str(base) + "_REPORT.md"),
        "keywords": Path(str(base) + "_keywords.txt"),
        "keywords_alt": folder / "keywords.txt",
        "text_extract": Path(str(base) + "_text_extract.txt"),
        "coverage": Path(str(base) + "_coverage.txt"),
        "visual_qa": Path(str(base) + "_visual_qa.png"),
        "visual_qa_alt": next(iter(sorted(folder.glob("visual_qa*.png"))), folder / "visual_qa.png"),
        "trace": folder / "decision_trace.json",
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("folder", type=Path)
    ap.add_argument("--pages", type=int, default=1)
    ap.add_argument("--max-bottom-ws", type=float, default=None)
    ap.add_argument("--min-bottom-ws", type=float, default=20.0)
    ap.add_argument("--max-right-ws", type=float, default=None)
    ap.add_argument("--allow-cpp", action="store_true")
    ap.add_argument("--json", default=None)
    ap.add_argument("--profile", type=Path, default=None)
    ap.add_argument("--master", type=Path, default=None)
    ap.add_argument("--bank", type=Path, default=None)
    ap.add_argument("--evidence", type=Path, default=None)
    ap.add_argument("--forbidden", type=Path, default=DEFAULT_FORBIDDEN)
    args = ap.parse_args()

    if not args.folder.is_dir():
        print(f"Job folder not found: {args.folder}", file=sys.stderr)
        return 66
    for tool in ("pdftotext", "pdfinfo"):
        if not shutil.which(tool):
            print(f"{tool} not installed (try: brew install poppler)", file=sys.stderr)
            return 69

    # Load personal facts from profile.yaml and build the personal patterns.
    profile = pl.load_profile(args.profile)
    root = pl.find_kit_root()
    paths = profile.get("paths", {})

    def resolve(arg, key):
        if arg is not None:
            return arg
        p = paths.get(key)
        return (root / p) if p else None

    master = resolve(args.master, "master_cv")
    bank = resolve(args.bank, "project_bank")
    evidence = resolve(args.evidence, "evidence_map")

    LANGUAGE_PATTERNS = pl.language_patterns(profile)
    CONTACT_PATTERNS = pl.contact_patterns(profile)
    EDUCATION_PATTERNS = pl.education_patterns(profile)
    EDU_ENTRY = pl.education_entry_pattern(profile)
    EXCLUSIONS = [e.lower() for e in pl.language_exclusions(profile)]

    files = discover(args.folder)
    gates = []

    g_files = Gate("files")
    gates.append(g_files)
    if files is None:
        g_files.fail("no PDF found in folder")
        report(args, gates, None)
        return 1

    for label, key in [(".tex", "tex"), ("_REPORT.md", "report")]:
        if not files[key].is_file():
            g_files.fail(f"missing {label}: {files[key].name}")
    if not (files["keywords"].is_file() or files["keywords_alt"].is_file()):
        g_files.fail("missing keywords file (<base>_keywords.txt or keywords.txt)")
    if not files["trace"].is_file():
        g_files.fail("missing decision_trace.json")

    text = pdf_text(files["pdf"])
    squashed = re.sub(r"\s+", " ", text).lower() if text else ""

    g_pages = Gate("pages")
    gates.append(g_pages)
    count = pdf_page_count(files["pdf"])
    if count is None:
        g_pages.fail("pdfinfo could not read page count")
    elif count != args.pages:
        g_pages.fail(f"page count {count}, expected {args.pages}")
    else:
        g_pages.info(f"{count} page(s)")

    g_overfull = Gate("overfull")
    gates.append(g_overfull)
    if files["log"].is_file():
        n = files["log"].read_text(errors="replace").count("Overfull \\hbox")
        if n:
            g_overfull.fail(f"{n} overfull hbox(es) in {files['log'].name}")
    else:
        g_overfull.warn(f"no .log next to PDF ({files['log'].name}); recompile to verify")

    g_cpp = Gate("cpp")
    gates.append(g_cpp)
    if text is None:
        g_cpp.fail("pdftotext failed")
    else:
        n = text.count("C++")
        if n and not args.allow_cpp:
            g_cpp.fail(f'"C++" appears {n}x (use --allow-cpp if the JD genuinely needs it)')
        elif n:
            g_cpp.info(f'"C++" appears {n}x (allowed via --allow-cpp)')

    g_lang = Gate("languages")
    gates.append(g_lang)
    if not LANGUAGE_PATTERNS:
        g_lang.warn("no languages in profile.yaml — skipped")
    for label, pat in LANGUAGE_PATTERNS.items():
        if not re.search(pat, squashed):
            g_lang.fail(f"missing: {label}")

    g_forbid = Gate("forbidden")
    gates.append(g_forbid)
    if args.forbidden.is_file():
        for line in args.forbidden.read_text(encoding="utf-8").splitlines():
            phrase = line.strip()
            if not phrase or phrase.startswith("#"):
                continue
            if phrase.lower() in squashed:
                g_forbid.fail(f'forbidden phrase present: "{phrase}"')
    else:
        g_forbid.warn(f"forbidden list not found: {args.forbidden}")
    for excl in EXCLUSIONS:  # languages you do not speak (from profile.yaml)
        if re.search(r"\b" + re.escape(excl) + r"\b", squashed):
            g_forbid.fail(f'excluded language present: "{excl}" (not in your profile)')

    tex_src = files["tex"].read_text(encoding="utf-8", errors="replace") if files["tex"].is_file() else ""
    profile_name = detect_profile(tex_src)

    g_contact = Gate("contact")
    gates.append(g_contact)
    if text is None:
        g_contact.fail("pdftotext failed")
    elif not CONTACT_PATTERNS:
        g_contact.warn("no contact info in profile.yaml — skipped")
    else:
        for label, pat in CONTACT_PATTERNS.items():
            if not re.search(pat, squashed):
                g_contact.fail(f"missing from header: {label} — do not collapse the header to links-only")
        if g_contact.status == "PASS":
            g_contact.info("phone + email present")

    g_edu = Gate("education")
    gates.append(g_edu)
    if text is None:
        g_edu.fail("pdftotext failed")
    elif not EDUCATION_PATTERNS:
        g_edu.warn("no education in profile.yaml — skipped")
    else:
        for label, pat in EDUCATION_PATTERNS.items():
            if not re.search(pat, squashed):
                g_edu.fail(f"missing/garbled: {label}")
        if EDU_ENTRY and re.search(re.escape(profile["education"]["institution"].lower()), tex_src.lower()) \
                and not re.search(EDU_ENTRY, tex_src):
            g_edu.warn(
                "Education not in canonical \\entry{...} form "
                "(freeform layout — degree wording may drift)"
            )
        if g_edu.status == "PASS":
            g_edu.info("canonical institution / degree line present")

    max_bottom = args.max_bottom_ws if args.max_bottom_ws is not None else (120.0 if profile_name == "dense" else 150.0)
    expected_right = 43.0 if profile_name == "dense" else 50.0
    max_right = args.max_right_ws if args.max_right_ws is not None else expected_right + 40.0
    margins = pdf_margins(files["pdf"])

    g_ws = Gate("bottom_ws")
    gates.append(g_ws)
    if margins is None:
        g_ws.warn("could not measure bottom whitespace")
    else:
        ws = margins["bottom"]
        if ws > max_bottom:
            g_ws.fail(f"bottom whitespace {ws:.1f}pt > max {max_bottom:.0f}pt ({profile_name}) — page too sparse")
        elif ws < args.min_bottom_ws:
            g_ws.fail(f"bottom whitespace {ws:.1f}pt < min {args.min_bottom_ws:.0f}pt (page too full)")
        else:
            g_ws.info(f"{ws:.1f}pt ({profile_name}, max {max_bottom:.0f})")

    g_right = Gate("right_ws")
    gates.append(g_right)
    if margins is None:
        g_right.warn("could not measure right whitespace")
    elif margins["right"] > max_right:
        g_right.fail(
            f"right whitespace {margins['right']:.1f}pt > max {max_right:.0f}pt — "
            f"text not filling the column (check template \\geometry timing)")
    else:
        g_right.info(f"{margins['right']:.1f}pt (expected ~{expected_right:.0f})")

    g_subset = Gate("numeric_subset")
    gates.append(g_subset)
    if files["tex"].is_file():
        sources = ""
        for src in (master, bank, evidence):
            if src and Path(src).is_file():
                sources += Path(src).read_text(encoding="utf-8", errors="replace") + "\n"
            else:
                g_subset.warn(f"source missing: {src}")
        source_tokens = numeric_tokens(sources)
        body = tex_body(tex_src)
        unknown = sorted(numeric_tokens(body) - source_tokens)
        if unknown:
            g_subset.fail(
                "numeric claims not found in master/bank/evidence: " + ", ".join(unknown)
            )
        else:
            g_subset.info("all numeric claims trace to sources")
    else:
        g_subset.fail("no .tex to audit")

    g_stale = Gate("staleness")
    gates.append(g_stale)
    pdf_mtime = files["pdf"].stat().st_mtime
    for key in ("text_extract", "coverage"):
        f = files[key]
        if f.is_file() and f.stat().st_mtime < pdf_mtime:
            g_stale.warn(f"{f.name} is older than the PDF — re-extract before quoting")
    vqa = files["visual_qa"] if files["visual_qa"].is_file() else files["visual_qa_alt"]
    if vqa.is_file():
        if vqa.stat().st_mtime < pdf_mtime:
            g_stale.warn(f"{vqa.name} is older than the PDF — re-render visual QA")
    else:
        g_stale.warn("no visual QA png found")

    g_cov = Gate("coverage")
    gates.append(g_cov)
    kw = files["keywords"] if files["keywords"].is_file() else files["keywords_alt"]
    helper = TOOLS_DIR / "keyword_coverage.py"
    if kw.is_file() and helper.is_file():
        out = run([sys.executable, str(helper), str(files["pdf"]), str(kw)])
        for line in out.stdout.splitlines():
            if re.match(r"\s+\S.*\d+\s*/\s*\d+", line) or "missing:" in line:
                g_cov.info(line.strip())
    else:
        g_cov.warn("keywords file or keyword_coverage.py unavailable")

    code = report(args, gates, files)
    return code


def report(args, gates, files):
    width = max(len(g.name) for g in gates)
    print(f"\nQA gates — {args.folder}")
    print("=" * 64)
    failed = False
    for g in gates:
        mark = {"PASS": "✓", "WARN": "⚠", "FAIL": "✗"}[g.status]
        print(f"  {mark} {g.name:<{width}}  {g.status}")
        for note in g.notes:
            print(f"      {note}")
        failed = failed or g.status == "FAIL"
    print("=" * 64)
    verdict = "FAIL — fix and rerun" if failed else "PASS"
    print(f"  Overall: {verdict}\n")

    if args.json != "-" and files is not None:
        out_path = (
            Path(args.json)
            if args.json
            else files["pdf"].with_name(files["pdf"].stem + "_qa.json")
        )
        payload = {
            "folder": str(args.folder),
            "pdf": str(files["pdf"]),
            "overall": "FAIL" if failed else "PASS",
            "gates": [
                {"name": g.name, "status": g.status, "notes": g.notes} for g in gates
            ],
        }
        out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
        print(f"  JSON: {out_path}\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
