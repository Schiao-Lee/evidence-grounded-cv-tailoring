# Meta prompt — tailor your master CV to one specific job

Paste the block below to your AI agent (e.g. Claude Code, opened in the kit
folder so `CLAUDE.md` and `profile.yaml` are in context). Fill the `Inputs`
section first.

This pipeline keeps AI-generated CVs **truthful, verifiable, and one page**. Its
spine is two hard rules — the SUBSET RULE and the GAP RULE — backed by a
deterministic QA gate (`tools/qa_one_job.py`). Personal facts come from
`profile.yaml`; this prompt never hardcodes them.

```text
Tailor my MASTER LaTeX CV to one specific job opening. Produce a compiled PDF
and a coverage report. Do NOT overwrite the master.

Inputs (fill before running):
- TARGET_COMPANY:        <e.g. Acme Corp>
- TARGET_ROLE_TITLE:     <e.g. Data Analyst - Business Intelligence>
- TARGET_ROLE_FAMILY:    <leave blank for auto-detection; else one of the
                          families defined in family_bases/>
- PAGE_MODE:             one-page | two-page         (default: one-page)
- JD_PATH or JD_TEXT:    <local path to JD file, OR paste JD text inside <jd>...</jd>>

Sources of truth (DO NOT add facts outside these):
- profile.yaml          — my immutable facts (name, contact, education, languages, caution list)
- Master CV:            path from profile.yaml -> paths.master_cv
- Project bank:         path from profile.yaml -> paths.project_bank   (richer per-project bullets)
- Evidence map:         path from profile.yaml -> paths.evidence_map   (what each claim is backed by)
- Tailoring families:   family_bases/*.json   (per-role-family default selections)
- Visual style:         templates/visual_style_guide.md + templates/cv_style_classic_blue.tex

Hard rules (anti-hallucination — these override style preferences):
- SUBSET RULE: the tailored CV must contain ONLY items present in the master or
  project_bank. Never invent a new item to match a JD.
- GAP RULE: if the JD requires something the master lacks, leave it out and add it
  to the GAP_LIST. Never fabricate a tool, metric, employer, date, or outcome.
- CAUTION LIST: apply every line in profile.yaml -> caution_list verbatim. These
  are your immutable facts (correct dates, prototype-vs-production boundaries,
  certifications-not-yet-earned, etc.). Do not drift on any of them.
- LANGUAGES: use exactly the languages in profile.yaml -> languages, with their
  levels. Never add a language from profile.yaml -> language_exclusions.
- For ATS submissions: single-column LaTeX only; no multi-column, no graphics that
  break text extraction.
- Visual template rule (reproducibility): do NOT improvise styling. \input the
  template (templates/cv_style_classic_blue.tex) and set \CVStyleProfile:
   * dense    -> technical data/BI/engineering/AI roles.
   * balanced -> risk/compliance/business/stakeholder-heavy roles.
  One-page CVs must have no page number, use inline skill rows (\skillline, not
  wide tables), and cut content before reducing margins below the profile.

Writing style (truthful, lean, ATS-aware):
- Be truthful and objective to the experience in the master.
- Be specific rather than general; lead bullets with quantified outcomes when the
  master/project_bank actually has the number.
- Rewrite highlights using STAR structure, but do NOT mention STAR explicitly.
- Write to express, not impress. Active voice and strong verbs: Built, Designed,
  Implemented, Automated, Analyzed, Modeled, Visualized, Deployed, Validated.
- Prioritize relevance to THIS job over general achievements.

Header (emit BOTH contact lines; NEVER collapse to one). Build from profile.yaml:
    \namestyle{<candidate.name>}
    \headline{<role-tailored tagline>}
    \contactline{<candidate.phone_display> \;|\; \href{mailto:<candidate.email>}{<candidate.email>} \;|\; <candidate.location>}
    \contactline{\href{<candidate.linkedin>}{LinkedIn} \;|\; \href{<candidate.github>}{GitHub}}
  The phone + email + location line is MANDATORY on every CV, one-page included.
  (qa_one_job.py FAILs if phone or email is missing — a collapsed header is the
  classic way they get dropped.)

Education — fixed \entry format; never freeform, never paraphrase the degree.
Build from profile.yaml -> education:
    \section{Education}
    \entry{<education.institution>}{<education.dates>}{<education.degree>}{<location>}
    \entry{<education.prior_institution>}{<education.prior_dates>}{<education.prior_degree>}{<location>}
  Degree wording is FIXED to profile.yaml; do NOT rewrite to "Master's student" and
  do NOT append a per-job course list. One-page mode: keep the canonical primary
  \entry row (you MAY drop the prior degree to save space). (qa_one_job.py FAILs if
  the canonical institution/degree line is absent.)

Other content rules:
- Summary: prose only — no leading bold family-label prefix.
- Projects/pubs: clean bold title + italic-grey tech line; no inline repo links on
  one-page CVs.
- Inline emphasis: \hl{...} the ONE highest-impact metric/phrase per kept bullet.
- Skills: reuse fixed canonical category names; keep only JD-relevant rows; bare
  skill names (no "Python (pandas)" annotations).
- Never put \color{...} inside a \section{} title — it gets uppercased and breaks.

Execution model (single agent that can read/write files + run a terminal):
- YOU orchestrate, decide content/positioning, and review.
- YOU also run the filesystem / compile / QA steps yourself (Steps 7, 8, 8.5, 9.5)
  — do NOT claim "compiled successfully" or "gates passed" without actually
  running the command and showing its real output.
- HONESTY RULE: if any step is skipped or run differently than documented, say so
  explicitly in the _REPORT.md. Hiding a substitution is the one unacceptable move.

Pipeline:

Step 0 - Parse the JD.
- Read JD from JD_PATH or the <jd>...</jd> block.
- Emit two lists:
    <jd_must_have>...</jd_must_have>   - hard requirements (skills, tools, qualifications, domains)
    <jd_nice_to_have>...</jd_nice_to_have>
- If TARGET_ROLE_FAMILY is blank, choose one family and justify in one line.

Step 1 - Pick exactly ONE summary block matching the family. Delete the rest.

Step 2 - Select projects (4-6 in two-page, 3-4 in one-page).
- Keep only projects whose `% ROLE_TAGS:` intersect the target family.
- Reorder strongest-first.
- Per section: (a) analyze source bullets vs JD must-haves, (b) keep the
  strongest-evidence bullets for THIS job, (c) optimize wording within the subset rule.

Step 3 - For each kept project, choose bullet source:
- Default = the master's bullet.
- Pull a richer/alternate bullet from project_bank when the JD wants depth.
- Mark each bullet's origin with `% PROVENANCE: master|project_bank`.

Step 4 - Technical Skills row: keep ONLY rows the JD actually names.

Step 5 - Optional richer variants: use ONLY if the role calls for it.

Step 6 - Length cut.
- two-page: 1 summary, 4-6 projects, grouped skills, education, selected pubs, languages.
- one-page: 1 summary line, 3-4 projects with 1 bullet each, core skills only,
            canonical education \entry (primary required, prior optional), languages
            one-line. Use the template profile; do not drop below template margins.

Step 6.5 - Visual template gate.
- Read templates/visual_style_guide.md.
- \input templates/cv_style_classic_blue.tex (do not copy the master preamble).
- Select profile: dense for technical, balanced for business/compliance.
- One-page visual hard rules: \pagestyle{empty} via template; inline \skillline
  rows; each bullet 1-2 visual lines; 5-6 sections preferred; after compiling,
  render/check the first-page PNG against your reference look.

Step 7 - Compile (run it; do not claim success without running).
- Output dir: JOB_APPLICATIONS/<TARGET_COMPANY>/   (create if missing)
- Output files (slugify the role title: lowercase, spaces -> _, drop punctuation):
    CV_<NAME>_<TARGET_COMPANY>_<TARGET_ROLE_TITLE_SAFE>.tex
    CV_<NAME>_<TARGET_COMPANY>_<TARGET_ROLE_TITLE_SAFE>.pdf
- Compile with XeLaTeX; on error, fix the .tex and recompile until the PDF builds.
- Verify page count; if it exceeds PAGE_MODE, re-trim and recompile.

Step 8 - Keyword-coverage gate.
- Write the must-have / nice-to-have lists from Step 0 into a keywords.txt next to
  the PDF (format: `# must-have` / terms / `# nice-to-have` / terms), then run:
    python3 tools/keyword_coverage.py <pdf> <keywords.txt>
- Use its output verbatim as coverage_must_have / coverage_nice_to_have.
- For each missing MUST-HAVE term:
    (a) master/project_bank HAS it but it was cut -> RE-ADD and recompile.
    (b) master/project_bank LACKS it -> add to GAP_LIST. Do NOT fabricate.

Step 8.5 - Deterministic QA gate (MANDATORY).
- Run: python3 tools/qa_one_job.py <job_folder>
- ALL gates must PASS (exit 0). On any FAIL: fix the .tex or the missing artifact,
  recompile, rerun. Never report completion with a failing gate.
- Paste the script's printed gate table verbatim into the _REPORT.md. WARNs must be
  resolved or explained.
- If a forbidden phrase is genuinely required by the JD, surface it to me instead of
  rewording to evade the gate.

Step 9 - Subset audit.
- RE-READ the master .tex and project_bank from disk FIRST (don't audit against your
  in-context memory — long sessions distort it).
- Diff every concrete claim (employer, date, metric, tool, project name, link)
  against master + project_bank. Anything not present -> SUBSET_VIOLATIONS; fix or
  remove, recompile. Definition of done requires SUBSET_VIOLATIONS empty.

Step 9.5 - Phone-interview prep (MANDATORY — separate folder).
- For EVERY generated CV, create exactly ONE prep file in the TOP-LEVEL
  PHONE_INTERVIEW_PREP/ folder, named <row_id>_<Company>_<Role_Slug>_prep.md,
  copying PHONE_INTERVIEW_PREP/_TEMPLATE.md.
- Fill: tailored-CV path, role angle, 60-second pitch, 2 project stories, likely
  questions, and the honesty/gap guardrails (reuse THIS run's GAP_LIST so a sudden
  call never overclaims).
- Verify: python3 tools/check_phone_prep.py reports this row covered.

Outputs (in JOB_APPLICATIONS/<TARGET_COMPANY>/ unless noted):
- CV_<NAME>_<TARGET_COMPANY>_<ROLE_SAFE>.tex / .pdf
- CV_<NAME>_<TARGET_COMPANY>_<ROLE_SAFE>_keywords.txt   (Step 8 input, saved)
- decision_trace.json   (Steps 0-6 decisions; REQUIRED — the files gate fails without it)
- visual_qa.png   (first-page render for the visual gate)
- CV_<NAME>_<TARGET_COMPANY>_<ROLE_SAFE>_REPORT.md containing:
    1. Target role family + 1-line justification.
    2. Must-have coverage X/N + missing must-haves.
    3. Nice-to-have coverage Y/N + missing nice-to-haves.
    4. GAP_LIST (items the master can't back up).
    5. SUBSET_VIOLATIONS (must be empty by completion).
    6. Page count + LaTeX engine + the real compile output snippet.
    7. Visual profile used + visual QA notes.
- Phone prep: PHONE_INTERVIEW_PREP/<row_id>_..._prep.md

Definition of done:
- PDF compiles cleanly with XeLaTeX; the real engine output is shown.
- Page count matches PAGE_MODE.
- qa_one_job.py exits 0; its gate table is pasted verbatim into the _REPORT.md.
- A phone-prep file exists for this row (check_phone_prep.py reports it covered).
- SUBSET_VIOLATIONS is empty.
- coverage_must_have is reported honestly; gaps are surfaced in GAP_LIST, not patched
  with invented content.
- The master .tex was NOT touched.
```
