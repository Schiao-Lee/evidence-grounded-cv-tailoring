# Start Here · Beginner's guide

> 🌐 English | [中文](START_HERE_zh.md)

> This guide is for first-time users. You **don't need to know how to code** — you
> just talk to the AI in plain language and hold one line.

---

## Remember this one thing first (most important)

This is **not** a "make my CV sound better" button. Its whole value is: **every
line is true and traceable.**

If a job asks for something you don't have, it records it as an honest *gap* — it
**never invents it for you**. The more honest you are, the more it helps. Remember:

> **When it wants to "round up," your job is to say "no." Leave the rest to it.**

---

## Step 0: Install the environment (the only thing you set up by hand)

This is the step non-technical users get stuck on. You need, on your machine:

- **Claude Code** (the tool you talk to the AI through; needs a Claude account)
- **XeLaTeX** (typesets the CV into a PDF)
- **poppler** (checks the PDF)

Exact install commands are in `README.md` → *Prerequisites* (copy the macOS lines).

> 💡 Tip: have **a friend who's done it sit with you once** (in person or screen
> share) for this step. Once the kit folder is open, the rest is all conversation
> and you can drive it yourself.

When ready: open Claude Code and confirm it's opened the `cv-workflow-kit` folder.
Then start with the four prompts below.

---

## The opening four prompts (in order, copy-paste one at a time)

### ① Get to know it + self-check (don't change anything yet)

```
First read README.md and CLAUDE.md in this folder, then tell me in plain language:
1) what this tool actually does;
2) what my computer is still missing to run it (check whether XeLaTeX and poppler
   are installed);
3) what information about myself I need to provide.
Don't make any changes yet.
```

### ② Dry-run on the "fake person" (build confidence + verify the install)

```
Using examples/toy_profile as the profile and examples/toy_jds/data_analyst.txt as
the JD, run the prompts/tailor_per_job.md pipeline end to end, and show me the QA
gate result table at the end. This is a synthetic test — do not touch my real info.
```

Seeing a fake CV get generated and all QA checks PASS shows you what the whole
process looks like.

### ③ Build your own data (the core step)

```
Now help me set up my own data. Follow BOOTSTRAP.md and interview me step by step,
starting from Step A. Follow the honesty rules in CLAUDE.md strictly: record only
true, evidenced facts. If I'm vague or exaggerate, push back or stop me.
```

The AI interviews you item by item (name, contact, education, languages, projects…).
You just **answer honestly**, and it builds your data (profile + your "master CV").

### ④ Tailor your first real job

```
I want to apply to a real job, using prompts/tailor_per_job.md.
Company, role, and JD are here: [paste the posting]
Keep going until qa_one_job.py is all PASS; ask me whenever you need me to decide.
```

---

## How to talk to it (3 rules are enough)

1. **It asks, you answer honestly.** If you're unsure, say so — don't guess.
2. **Stop it when it exaggerates.** If it turns a "course project" into a "production
   system," say: "that was a course project, change it back."
3. **The QA gate is the judge.** A CV is only done when `qa_one_job.py` is **all
   PASS**; if it isn't, tell it to keep fixing.

---

## Day-to-day use

Setup happens once (prompts ①②③). After that, for every new job you **only use
prompt ④**: swap the company and JD, run it until the QA gate is all green.

Each finished CV also gets a phone-interview cheat sheet in `PHONE_INTERVIEW_PREP/`
(including how to answer gaps honestly), so a surprise call never makes you bluff.

> 🚀 **Advanced (look once you're comfortable):** want to apply to many jobs at once?
> Paste a pile of LinkedIn JDs into one file and run batch mode, one job per row —
> see `prompts/batch_driver.md`. Ignore it at first; get single jobs smooth first.

---

## What's in the kit (a rough idea is enough)

You'll mostly only touch `profile.yaml` and your CV; the rest is for the AI.

| You'll touch | What it is |
|--------------|------------|
| `profile.yaml` | **Your fact card**: name, contact, education, languages, and your "things I'll never exaggerate" list. Built once at setup, updated occasionally |
| your "master CV" in `MASTER_CV/` | The full set of **everything** you've done. Each application is **cut down** from it; nothing new is ever added |
| `JOB_APPLICATIONS/<Company>/` | One folder per application, holding the tailored CV PDF + report |
| `PHONE_INTERVIEW_PREP/` | One phone-interview cheat sheet per CV |

| What the AI uses (you can ignore) | What it is |
|-----------------------------------|------------|
| `CLAUDE.md` | The rules for the AI (honesty-first, must pass QA) |
| `prompts/tailor_per_job.md` | The full pipeline for tailoring one job |
| `BOOTSTRAP.md` | The interview script that builds your data the first time |
| `tools/` | The QA scripts (`qa_one_job.py`, etc.) |
| `examples/` | Synthetic samples for practice |

---

## How to read the QA gate

After each CV, the AI prints a table — one check per row, three outcomes:

- **✓ PASS** — passed
- **⚠ WARN** — a heads-up, not fatal, but have the AI explain it
- **✗ FAIL** — **not passed; this CV is not done.** Make the AI fix it until all green

The checks fall into four groups; you don't need to read English to know "what a red
one roughly means":

| Group | Checks | A red one usually means |
|-------|--------|-------------------------|
| **Truthfulness** (most important) | `numeric_subset` | A number appears that isn't in your master CV → likely the AI made one up; have it remove or correct it |
| | `forbidden` | Self-undermining phrasing ("still learning," "limited experience"), or a language you don't speak |
| | `languages` / `contact` / `education` | Your languages, phone/email, or degree didn't appear correctly (or got rewritten) |
| **Layout** | `pages` | Wrong page count (wanted 1, got 2) → have it cut more |
| | `overfull` / `bottom_ws` / `right_ws` | Text overflow or too much empty space → have it adjust |
| **Files present** | `files` | A report, keywords, or decision-trace file is missing |
| **Coverage** | `coverage` | Just tells you JD keyword coverage — not an error |

**What you do is simple: see any ✗, tell the AI "this gate didn't pass, fix it and
give it back."** Pay extra attention when a truthfulness check (especially
`numeric_subset`, `forbidden`) goes red — that's often the AI trying to exaggerate
and being caught, which is exactly the point of this tool.

---

## What to do when something breaks (just say it)

Don't debug it yourself — describe what you see and let the AI handle it. Common ones:

- **Install stuck / a command errors** → go back to "Step 0" and have a helper sit
  with you to install Claude Code, XeLaTeX, and poppler. Nothing runs until this works.
- **AI says "compile failed / xelatex error"** → say: "the compile errored, look at
  the log, fix the .tex and recompile until the PDF is produced."
- **A gate keeps FAILing** → "this gate is still red — tell me exactly what's not
  satisfied, then fix it."
- **It turns a course project into a production system / inflates a level** → "that's
  an exaggeration, change it back to the true wording and add the missing skill to GAP_LIST."
- **It says "compiled / passed" but didn't show you the command output** → "please
  actually run qa_one_job.py and paste its printed table verbatim." (The rules
  require it to really run things, not just claim it.)

---

## When is a CV "done"?

All of the following (have the AI confirm against them):

1. The PDF compiles, page count is right (usually 1);
2. `qa_one_job.py` is **all PASS** (WARNs explained), the table pasted into the report;
3. `SUBSET_VIOLATIONS` in the report is empty (nothing unsupported);
4. Anything the JD wants that you lack is honestly listed in `GAP_LIST` (not invented);
5. This CV has a matching cheat sheet in `PHONE_INTERVIEW_PREP/`.

---

## Your data, your privacy

- **Everything runs on your own computer.** Your CV and data are not uploaded
  anywhere, and the tool's author never sees them.
- `profile.yaml` and your "never exaggerate" list are **yours** — only you decide
  what's true and what to leave out.
- To change info (new phone, a new experience), just edit `profile.yaml` or have the
  AI update your "master CV"; the next application picks it up automatically.

---

## FAQ

**Can I talk to it in my own language?** Yes — it understands many languages. The
kit's docs are in English, but those are for the AI to read.

**Does it cost money?** Claude Code needs a Claude account (subscription or API).
XeLaTeX and poppler are free.

**I don't have a finished CV yet — can I use it?** Yes. Prompt ③ (BOOTSTRAP) is the
AI interviewing you and building your "master CV" from scratch.

**Where are my finished CVs?** In `JOB_APPLICATIONS/<Company>/`; the `.pdf` is the result.

**Will it auto-apply for me?** No. It only generates CVs and interview cheat sheets;
whether and where you apply is entirely up to you.

---

## In one line

> Once it's installed, you only ever talk to it in plain language. Paste the first
> three prompts to set up, then use prompt ④ for every job. When it tries to
> fabricate, you say "no" — leave the rest to it.
