# CV Tailoring Workflow Kit

> 🇨🇳 第一次用、想要中文上手指南?看 **[START_HERE_zh.md](START_HERE_zh.md)**。

A human-in-the-loop workflow that turns **your master CV + a job description**
into a **truthful, ATS-clean, one-page tailored CV** — every claim traceable to
source, checked by a deterministic QA gate, never invented to match the JD.

Your data stays on your machine. Nothing personal is hardcoded in the scripts —
your facts live in one file, `profile.yaml`.

> **Status:** working prototype. All examples are synthetic. Built as a case study
> in keeping AI-generated documents truthful and verifiable.

## What this project demonstrates

A small but complete example of **trustworthy, human-in-the-loop document
generation** — the kind of guardrails real AI/automation work needs:

- **Anti-hallucination by construction** — two hard rules (a *subset rule*: output
  only facts present in the source; a *gap rule*: missing requirements become an
  explicit gap, never an invention) instead of hoping the model behaves.
- **Deterministic QA gates, not LLM self-report** — `qa_one_job.py` runs 13
  machine checks (numeric claims trace to source, required contact/education/
  language present, forbidden/confessional phrasing, page count, overfull boxes,
  whitespace, artifact completeness…) and blocks "done" until they pass.
- **Config-as-data** — zero personal facts in code; one `profile.yaml` drives every
  personalized check, so the same engine fits anyone.
- **Evidence-grounded** — a master CV + project bank + evidence map are the only
  sources of truth; tailored CVs are disposable derived artifacts.
- **Verification-first rendering** — XeLaTeX compile + `pdftotext`/`pdfinfo`/`pdftoppm`
  audits + keyword-coverage checks, all run for real (no "compiled successfully"
  claims without the command output).
- **Reproducible batch processing** — deterministic JD splitting feeds a resumable,
  one-row-per-run console (`jobs.csv`) with staleness detection.

## How it works

Three deliberately separated layers (so no single prompt owns everything):

1. **Evidence** — `profile.yaml` + master CV + project bank + evidence map: what may be said.
2. **Decision** — `prompts/tailor_per_job.md`: role-family classification, JD must/nice
   extraction, project & bullet selection under the subset rule, gap-list generation.
   Decisions are saved to `decision_trace.json` for explainability.
3. **Presentation** — `templates/` LaTeX visual system (dense/balanced profiles).

Each job runs Steps 0→9.5: parse JD → select content → render → keyword gate →
**deterministic QA gate** → subset audit → phone-prep. An agent that can read/write
files and run a terminal (e.g. Claude Code) orchestrates and executes it.

## What's in here

```
profile.example.yaml   <- copy to profile.yaml and fill in YOUR facts (the only setup)
CLAUDE.md              <- the rules your AI follows (auto-loaded by Claude Code)
BOOTSTRAP.md           <- one-time setup: AI interviews you and builds your master CV
prompts/tailor_per_job.md   <- the per-job pipeline you use day to day
tools/                 <- the gates (qa_one_job.py is mandatory) + profile loader
templates/             <- the LaTeX visual system
family_bases/          <- per-role-family defaults (see SCHEMA.md)
examples/              <- a SYNTHETIC toy profile + JDs to learn on (safe to run)
MASTER_CV/ JOB_APPLICATIONS/ PHONE_INTERVIEW_PREP/   <- your working folders (empty)
```

## Prerequisites

| Need | Why | Install (macOS) |
|------|-----|------|
| An AI coding agent | runs the workflow | **Claude Code** recommended — `npm i -g @anthropic-ai/claude-code` (needs a Claude subscription or API key) |
| Python 3.9+ | the QA scripts | preinstalled on macOS; PyYAML optional (`pip install pyyaml`) — there's a built-in fallback parser if it's missing |
| Poppler (`pdftotext`, `pdfinfo`, `pdftoppm`) | PDF checks | `brew install poppler` |
| XeLaTeX | compiles the CV | `brew install --cask mactex` (or `basictex`) |

Quick check: `pdftotext -v` and `xelatex --version` should both print a version.

## Does it have to be Claude?

No. The **content** of `CLAUDE.md` is plain instructions — not tied to any vendor.
Only the auto-load filename differs:

- **Claude Code** — keep it as `CLAUDE.md` (loads automatically). Recommended,
  because this kit is built around an agent that can read/write files and run a
  terminal, which Claude Code does natively.
- **Codex CLI** — rename `CLAUDE.md` to `AGENTS.md`.
- **A web chat (no file/terminal access)** — works, but you'll run the Python QA
  steps by hand, so the quality gate is easy to skip. Not recommended.

The Python tools run the same regardless of which agent you use.

## Getting started (15 minutes)

1. **Try the toy first.** Open this folder in Claude Code and say:
   > "Using examples/toy_profile as the profile and examples/toy_jds/data_analyst.txt
   > as the JD, run prompts/tailor_per_job.md end to end and show me the QA gate."

   This proves the toolchain works without touching your data.

2. **Make it yours.** Copy `profile.example.yaml` → `profile.yaml` and fill it in,
   then open `BOOTSTRAP.md` and paste its block to the agent. It interviews you and
   builds your master CV, project bank, evidence map, and role families.

3. **Use it per job.** For each application, open `prompts/tailor_per_job.md`, fill
   the Inputs (company, role, JD), and follow Steps 0 → 9.5. Done means
   `python3 tools/qa_one_job.py <job_folder>` exits 0 and its table is pasted into
   the report.

## The honesty rule (read this once)

This kit is deliberately **not** a "make my CV sound better" button. Its whole
point is that every line is true and traceable. If a JD wants a skill you don't
have, the workflow records it as a *gap* — it never invents it. Used that way it
makes you faster and more honest at once. Used to fabricate, it just adds a QA
gate that you'd have to fight. Don't fight it.

## Batch mode (optional, once you're comfortable)

To tailor many jobs from one pile of JDs, see **[prompts/batch_driver.md](prompts/batch_driver.md)**:

1. `python3 tools/jd_autosplit.py JOB_APPLICATIONS/_intake/jds_<Date>` splits a raw
   LinkedIn dump into clean per-job files and seeds a `jobs.csv` console.
2. The batch driver processes **one row per run** (resumable, one CV at a time),
   running the same Step 0–9.5 pipeline + QA gate for each.
3. `tools/build_jobs_master.py` aggregates every batch into one console;
   `tools/check_phone_prep.py` verifies every CV has phone prep.

Try the splitter now (writes nothing):
```bash
python3 tools/jd_autosplit.py examples/toy_jds/linkedin_dump_example.txt --dry-run
```

## Privacy & ethics

- **Your data is local.** The workflow runs on your machine; nothing is uploaded.
- **The examples are synthetic.** `examples/toy_profile` is a fictional person
  (Alex Kowalski). No real applicant data ships in this repo.
- **A scanner enforces that.** `python3 tools/redact_scan.py` checks the tree for
  leaked emails, phone numbers, absolute home paths, and key-like tokens before
  you ever publish or share a copy.
- **It's for truthful tailoring, not fabrication.** The whole design exists to make
  honest selection faster — not to help anyone overstate. The gates fight fabrication
  on purpose.

## Project status

Working prototype / portfolio case study. The single-job and batch pipelines run
end to end (verified: synthetic master CV compiles clean, all profile-driven gates
pass). Possible next steps: tests + CI, a thin Python runner, more role-family bases.

## License

MIT — see [LICENSE](LICENSE).

## Not included (ask if you want it)

- A pre-compiled demo PDF — the toy profile is the *input*; you generate the
  output yourself so you see the whole pipeline run.
