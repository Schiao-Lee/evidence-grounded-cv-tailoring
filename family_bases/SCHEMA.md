# Role-family bases

A **role family** is a cluster of similar jobs (e.g. all "data analyst / BI"
roles). Instead of re-deciding everything for each job, you write a *base* once
per family — your default summary, default project ranking, default skill rows —
and each concrete job just applies a small JD-specific overlay on top.

This is what lets you tailor 20 jobs without 20 blank-page decisions.

## How to use

1. Decide your families (5–8 is typical). Common ones:
   `data-analyst-bi`, `data-science-ml`, `data-engineering`,
   `risk-compliance`, `business-strategy`, `ai-enablement`.
2. For each family, copy `data-analyst-bi.base.example.json` to
   `<family>.base.json` and fill it from YOUR master CV / project bank.
3. When tailoring (see `prompts/tailor_per_job.md`), the AI picks the matching
   family base, then overlays the job's must-haves/nice-to-haves.

## Schema

| Field | Meaning |
|-------|---------|
| `role_family` | the family id (matches the filename) |
| `visual_profile` | `dense` or `balanced` (see templates/visual_style_guide.md) |
| `default_page_mode` | `one-page` or `two-page` |
| `summary_source` | which summary block to use for this family |
| `default_projects_ranked` | your projects, strongest-first, for this family |
| `default_experience` | which work entries to include by default |
| `default_skill_rows` | which skill category rows to show |
| `common_keywords` | terms these JDs usually ask for (sanity-check coverage) |
| `common_gaps` | things you usually lack here → likely GAP_LIST items |
| `job_overlay_fields` | the per-job fields layered on top of this base |

> All project/skill names must come from YOUR master CV or project bank — the
> base is a *selection* of real items, never an invention of new ones.
