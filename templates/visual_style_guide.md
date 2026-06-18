# Classic Blue CV Visual System

Purpose: make tailored CVs visually consistent. Content selection, keyword coverage, and subset audit remain separate; this file defines the reusable layout rules so the AI does not improvise aesthetics per job.

## Two profiles

- **Dense** (`\CVStyleProfile{dense}`)
  - Compact, strong technical density, still structured and readable.
  - Best for: data analyst/BI, data engineering, AI/ML, technical roles.
  - Margin target ~0.60in, body ~9.5pt.
- **Balanced** (`\CVStyleProfile{balanced}`)
  - More whitespace, steadier business-facing feel.
  - Best for: risk/compliance, banking, strategy, stakeholder-facing internships.
  - Margin target ~0.70in, body 10pt.

> Tip: once you have produced one CV you are happy with in each profile, keep those two PDFs as your personal "reference looks" and compare new outputs against them.

## Why the references look good

1. **Stable hierarchy**
   - Name: uppercase, blue, letter-spaced.
   - Tagline/contact: smaller and lighter; they do not compete with the body.
   - Section headings: uppercase blue, letter-spaced, thin blue rule.
   - Entry/project titles: black bold; dates and tool stacks grey/italic.

2. **Consistent blocks**
   - Every project: title -> grey italic stack -> 1–2 concise bullets.
   - Stable indentation and controlled spacing.

3. **Controlled density**
   - Dense ≠ random compression. Margins, font size, line height, and bullet length are all bounded.
   - Do not drop margins below the template minimum just to force one page — cut content first.

4. **Inline skills**
   - One-page CVs use `Skill category: tools...` inline lines (`\skillline`).
   - Avoid wide two-column `tabularx` skills blocks (labels wrap and look broken).

5. **No one-page page number**
   - One-page CVs use `\pagestyle{empty}`. A lone page number makes the CV look like a report.

## Visual QA gate for every tailored CV

Run after LaTeX compiles and keyword/subset checks pass:

1. **Page style** — one-page mode: no page number (`\pagestyle{empty}` via template).
2. **Margin discipline** — do not reduce below the profile. If it does not fit, cut content first.
3. **Bullet length** — target 1–2 visual lines per bullet. A paragraph bullet means trim wording.
4. **Section count** — one-page target 5–6 sections. If 7+, merge `Skills`/`Languages` or inline languages.
5. **Skills format** — prefer `\skillline{...}{...}`; avoid label columns that wrap.
6. **Visual reference check** — render page 1 to PNG (`pdftoppm -png -f 1 -singlefile -r 150`) and compare against your reference look: header height, rule weight, body width, project spacing, bottom whitespace.
7. **ATS/text extraction wins** — single-column only. No graphics, icons, sidebars, or two-column layouts that harm `pdftotext`.

## Agent rule

The AI may select content, shorten bullets, and choose `dense` vs `balanced`. The AI should NOT hand-edit core visual macros unless explicitly asked to revise the design system itself.
