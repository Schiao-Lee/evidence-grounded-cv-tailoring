# What a finished application looks like

After you run `prompts/tailor_per_job.md` for one job, the job folder
`JOB_APPLICATIONS/<Company>/` should contain:

```
CV_<Name>_<Company>_<Role>.tex          # the tailored source
CV_<Name>_<Company>_<Role>.pdf          # compiled, correct page count
CV_<Name>_<Company>_<Role>.log          # XeLaTeX log (QA checks it for overfull boxes)
CV_<Name>_<Company>_<Role>_keywords.txt # the must/nice-have terms used for coverage
CV_<Name>_<Company>_<Role>_REPORT.md    # coverage, GAP_LIST, subset audit, the QA gate table
CV_<Name>_<Company>_<Role>_qa.json      # machine-readable QA result (written by qa_one_job.py)
decision_trace.json                     # the selection decisions (required by the files gate)
visual_qa.png                           # first-page render for the visual check
```

Plus, in the top-level `PHONE_INTERVIEW_PREP/` folder:

```
<row_id>_<Company>_<Role>_prep.md       # honesty/gap guardrails + likely questions
```

**Definition of done** = `python3 tools/qa_one_job.py JOB_APPLICATIONS/<Company>`
exits 0, every gate is PASS (WARNs explained in the report), `SUBSET_VIOLATIONS`
is empty, and gaps are listed honestly in the `_REPORT.md` rather than invented.

To generate a real example here, run the toy from the README:
> "Using examples/toy_profile as the profile and examples/toy_jds/data_analyst.txt
> as the JD, run prompts/tailor_per_job.md end to end and show me the QA gate."
