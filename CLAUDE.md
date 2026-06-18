# CV Tailoring Workflow — agent instructions

This file is auto-loaded by Claude Code when you open this folder. It is the
"brain" of the workflow: the rules an AI must follow when tailoring a CV here.
(Using a different agent? See README.md — rename this to `AGENTS.md` for Codex,
or paste it as a system prompt for a web chat.)

## What this workspace does

Turn a **master CV + a job description** into a **truthful, ATS-clean, one-page
tailored CV** — every claim traceable to source, verified by a deterministic QA
gate, never fabricated to match the JD.

This is human-in-the-loop tailoring, **not** an "optimize my CV" button and
**not** a fabrication tool. If the JD wants something the candidate doesn't have,
that goes on a gap list — it does not get invented.

## The one non-negotiable: honesty-first

Two hard rules override every style preference:

- **SUBSET RULE** — the tailored CV contains ONLY items present in the master CV
  or project bank. Never invent a tool, metric, employer, date, or outcome.
- **GAP RULE** — if the JD needs something the master lacks, leave it out and add
  it to the `GAP_LIST` in the report. Surfacing a gap is a success, not a failure.

Plus the candidate's own **caution list** (`profile.yaml` → `caution_list`):
immutable personal facts (correct dates, prototype-vs-production boundaries,
not-yet-earned certifications). Apply every line verbatim; never drift.

If you are ever tempted to "round up" to match a JD — stop, and write a GAP
instead. A rejected-but-honest CV is the correct output.

## Personal facts live in profile.yaml — never hardcode them

`profile.yaml` holds the candidate's name, contact, education, languages, and
caution list. The QA gate and the prompts read from it. When you build the header
or education block, pull values from `profile.yaml`; do not paste literals.

## Folder layout

- `profile.yaml` — the candidate's immutable facts (they fill `profile.example.yaml`).
- `MASTER_CV/current/master_cv.tex` — the editable source of truth (LaTeX). PDFs
  are compiled outputs only. **Never overwrite the master during tailoring.**
- `MASTER_CV/project_bank/project_bank.md` — richer per-project bullets to pull from.
- `MASTER_CV/checkpoints/evidence_map.md` — what each claim is backed by.
- `prompts/tailor_per_job.md` — the full tailoring pipeline (Steps 0–9.5). This is
  the procedure to run for one job.
- `prompts/batch_driver.md` — optional batch mode: split a JD pile with
  `tools/jd_autosplit.py`, then process one `jobs.csv` row per run (resumable).
- `family_bases/*.json` — per-role-family default selections (see SCHEMA.md).
- `templates/` — `cv_style_classic_blue.tex` (visual system) + `visual_style_guide.md`.
- `tools/` — the gates: `qa_one_job.py` (mandatory), `keyword_coverage.py`,
  `check_phone_prep.py`, `build_jobs_master.py`, `profile_loader.py`.
- `JOB_APPLICATIONS/<Company>/` — one folder per application (tex, pdf, report,
  keywords, decision_trace.json, visual_qa.png).
- `PHONE_INTERVIEW_PREP/` — one prep file per generated CV (top-level).
- `examples/` — a synthetic toy profile + JDs to learn on (safe to run).

## Workflow rules

1. Never overwrite `MASTER_CV/current/master_cv.tex` while tailoring a job.
2. Keep unresolved facts as `TODO_VERIFY` in the `.tex` while drafting; they must
   not survive into a final PDF (the QA gate forbids them).
3. For final tailoring, cut from the master `.tex` using `% ROLE_TAGS:` comments
   and the project bank — never add facts from outside master + project_bank.
4. `\input` the visual template; never hand-roll the preamble (that is what drops
   the contact line and garbles Education).
5. **Every tailored CV must pass `python3 tools/qa_one_job.py <job_folder>`
   (exit 0) before you report it done.** Paste the real gate table into the
   `_REPORT.md`. Do not assert "gates passed" without running it.
6. Every generated CV needs a phone-prep file — verify with
   `python3 tools/check_phone_prep.py`.
7. Run filesystem / compile / QA steps for real. If you skip or substitute a step,
   say so explicitly in the report. Hiding a substitution is the one unacceptable move.

## To tailor one job

Open `prompts/tailor_per_job.md`, fill the Inputs, and follow Steps 0 → 9.5.
That file is authoritative for the procedure; this file is authoritative for the
principles.

## First-time setup

If `profile.yaml` and `MASTER_CV/current/master_cv.tex` don't exist yet, the
candidate hasn't onboarded. Point them to `BOOTSTRAP.md` (or run it with them).
