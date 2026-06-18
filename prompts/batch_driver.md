# Batch driver — process ONE jobs.csv row per run

Tailor many jobs from one pile of JDs, **one row at a time**. The per-row loop is
deliberately *not* "do everything at once": one run = one CV, then stop. That makes
it resumable (a crash continues from the unfinished row), reviewable, and bounded
(one full Step 0–9.5 run fits comfortably in a single agent session; two do not).

Prerequisite: you've finished `BOOTSTRAP.md` (profile + master CV + family bases).

## Before the batch: automatic split + clean (once per JD pile)

Paste raw LinkedIn job pages (noise and all) into
`JOB_APPLICATIONS/_intake/jds_<Date>`, then run:

```bash
python3 tools/jd_autosplit.py JOB_APPLICATIONS/_intake/jds_<Date> --dry-run   # preview
python3 tools/jd_autosplit.py JOB_APPLICATIONS/_intake/jds_<Date>             # for real
```

It detects job boundaries, strips LinkedIn UI noise, writes numbered
`_jds_<Date>/NNN_Company_Role.txt` files (ids continue across batches), and seeds
`batch_runs/<date>_<label>_v1/jobs.csv` with `pending` rows.

> Not a LinkedIn dump? Just create the per-job `.txt` files and a `jobs.csv` by
> hand (columns: `id,company,role,role_family,page_mode,jd_file,status`). The
> driver below only needs `jobs.csv`.

Open `jobs.csv` and, per row, set `page_mode` (one-page / two-page) and optionally
`role_family`. Leaving `page_mode` blank is intentional friction — the driver
refuses to guess it.

## Per row (paste this to your agent; run it once per row)

Fill `<BATCH_DIR>` (e.g. `JOB_APPLICATIONS/batch_runs/2026-06-13_jun13_v1`) and paste:

```text
Process exactly ONE pending row of the CV tailoring batch, end to end. Read CLAUDE.md
first for the honesty rules.

1. Read <BATCH_DIR>/jobs.csv. Pick the FIRST row whose status is `pending`
   (or a stale `running` row that has no output_pdf — a prior crash; resume it)
   (or the row id I name here: <ROW_ID or blank>). Set its status to `running`
   and SAVE the csv before doing anything else.
2. Read the JD file from that row's jd_file column. If the file is missing, mark
   the row failed_no_jd, save, and STOP.
3. Execute the full pipeline from prompts/tailor_per_job.md for this one job —
   ALL of Steps 0 through 9.5, including BOTH Step 8.5 (QA gate) and Step 9.5
   (phone-interview prep):
   - TARGET_COMPANY / TARGET_ROLE_TITLE from the row's company/role columns
   - TARGET_ROLE_FAMILY from the row if set, else auto-detect
   - PAGE_MODE from the row's page_mode column; if it is blank, mark the row
     failed_no_page_mode and STOP — do NOT silently default.
   All hard rules, sources of truth, and the Definition of done in that file apply.
4. Step 8.5 is mandatory: run
   python3 tools/qa_one_job.py <job folder>
   and do not finish until it exits 0. Paste its gate table into the _REPORT.md.
   If you run any step differently than documented, say so in _REPORT.md.
5. Step 9.5 is mandatory: create/update ONE prep file in the TOP-LEVEL folder
   PHONE_INTERVIEW_PREP/<id>_<Company>_<Role>_prep.md (copy _TEMPLATE.md; reuse
   THIS run's GAP_LIST for the honesty guardrails), then run
   python3 tools/check_phone_prep.py --row <id>
   It MUST report the row as covered before you finish.
6. Update the row: status (done_verified / failed_*), output_pdf, must_have_cov,
   gaps, master_version, and any QA columns this csv uses. Save jobs.csv. THEN run
   python3 tools/build_jobs_master.py
   so the cross-batch console (JOB_APPLICATIONS/jobs_master.csv) never goes stale.
7. Report: row id, company, role family, coverage, GAP_LIST, QA verdict, PDF path,
   and the phone-prep path + check_phone_prep verdict. Then STOP — do NOT start the
   next row in this run.
```

Repeat the paste for each row (or say "do the next pending row"). Suggested `status`
values: `pending`, `running`, `done_verified`, `failed_compile`, `failed_subset`,
`failed_no_jd`, `failed_no_page_mode`, `needs_visual_review`, `stale_regenerate`,
`skip_low_fit`.

## Why one row per run (the three jobs jobs.csv does)

1. **Driver** — one row = one CV task.
2. **Checkpoint / resume** — interrupted runs continue from `pending`/`running` rows.
3. **Staleness** — `master_version` records which master/template made each output;
   when you improve the master, mismatched rows become `stale_regenerate`.

## Shortcut: family bases

Because jobs cluster into a few role families, fill `family_bases/<family>.base.json`
once (your default summary, projects, skills, profile). Then each job is a small
overlay on its family base instead of a blank-page decision — much faster and more
consistent within a family. Reserve full bespoke tailoring for high-priority roles.

## Iron rule

The master CV is the only source of truth; tailored CVs are derived artifacts you
can delete and regenerate. Never copy a nice sentence from one tailored CV into
another as if it were evidence — trace it to the master/project_bank or drop it.
If a generated CV is stale, mark the row `stale_regenerate`; never hand-patch a PDF.
