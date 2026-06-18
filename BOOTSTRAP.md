# BOOTSTRAP — first-run setup (paste this to your AI agent)

You only do this once. It turns the empty kit into *your* workflow by building
four things from your real history:

1. `profile.yaml` — your immutable facts
2. `MASTER_CV/current/master_cv.tex` — your full master CV (superset of everything)
3. `MASTER_CV/project_bank/project_bank.md` — detailed bullets per project/job
4. `MASTER_CV/checkpoints/evidence_map.md` — what backs each claim

Open this folder in Claude Code (so `CLAUDE.md` is loaded), then paste the block
below. Have your current CV / LinkedIn / transcripts handy — the agent will
interview you.

```text
You are helping me set up an evidence-grounded CV tailoring workspace. Read
CLAUDE.md first so you follow the honesty-first rules. Then walk me through
onboarding, ONE step at a time, asking me questions and waiting for my answers.

The single most important rule: we record only TRUE, evidenced facts. If I'm
vague, ask for specifics. If something was a prototype/course project, label it
as such. If I "round up", push back. A gap recorded honestly is a success.

Step A — profile.yaml
- Copy profile.example.yaml to profile.yaml.
- Interview me for: full name; phone; email; location; LinkedIn + GitHub URLs;
  highest degree (institution, exact degree wording, dates) and prior degree;
  every language with an honest CEFR-ish level; languages people assume I speak
  but I don't (-> language_exclusions).
- Build my caution_list: ask me for the facts I must never let a CV drift on —
  exact employment dates, what was prototype vs production, certifications not yet
  earned, anything I've seen misstated. Write each as one imperative line.
- Save profile.yaml. Then run `python3 tools/profile_loader.py` and show me the
  patterns it will enforce, so I can confirm they're right.

Step B — master CV (MASTER_CV/current/master_cv.tex)
- This is the SUPERSET: every job, project, skill, publication I might ever want
  to show. We tailor DOWN from it later; we never add beyond it.
- Use templates/cv_style_classic_blue.tex for layout (\input it; set
  \CVStyleProfile). Build the header and Education from profile.yaml.
- For each experience/project, ask me for: title, dates, what I actually did,
  tools, and any REAL metric. Add a `% ROLE_TAGS:` comment listing which role
  families it suits (e.g. data-analyst-bi, data-science-ml).
- Mark anything I'm unsure of as `% TODO_VERIFY` — do not assert it.
- Compile it with XeLaTeX and show me the PDF before moving on.

Step C — project_bank/project_bank.md
- For my strongest 3-6 projects, capture RICHER detail than fits on one page:
  dataset, methods, tools, metrics, outputs, and a one-line "tailoring angle".
- This is where the tailor prompt pulls extra depth when a JD wants it.

Step D — evidence_map.md
- For each non-obvious claim (metrics, scope, ownership), note what backs it
  (repo link, report, dashboard, manager confirmation). This is my honesty ledger.

Step E — role families
- Read family_bases/SCHEMA.md. Help me pick 5-8 families and, for each, copy the
  example to <family>.base.json and fill it by SELECTING real items from my master.

Step F — dry run
- Tailor my master to ONE of the synthetic JDs in examples/toy_jds/ following
  prompts/tailor_per_job.md, end to end, including the QA gate. Show me the gate
  table. This proves my setup works before I use it on a real job.

Begin with Step A. Ask me the first question now.
```

When this finishes you'll have a working, personalized workflow. From then on,
day to day, you only use `prompts/tailor_per_job.md` per job.
