# Phone-interview prep

One prep file per generated CV, named `<row_id>_<Company>_<Role_Slug>_prep.md`,
copied from `_TEMPLATE.md`. The row id matches your `jobs_master.csv` so coverage
can be checked by row.

Why it's a separate top-level folder: early-funnel phone screens move fast, and
you want the honesty/gap guardrails for a role written down *before* a recruiter
calls — so a surprise call never makes you overclaim.

Check coverage anytime:

```
python3 tools/check_phone_prep.py
```

It reports any generated CV (a job folder containing a `CV_*.pdf`) that has no
prep file yet.
