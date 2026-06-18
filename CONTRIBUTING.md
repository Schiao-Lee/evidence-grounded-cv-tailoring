# Contributing

Thanks for taking a look at this project. This repository is a working prototype
and portfolio case study for truthful, evidence-grounded CV tailoring.

## Ground rules

- Keep the project honesty-first: no feature should encourage fabricating CV
  claims, credentials, metrics, or experience.
- Do not include real personal CVs, job applications, phone numbers, emails, or
  employer-specific application details in issues, pull requests, fixtures, or
  examples.
- Use synthetic examples for tests and docs. The existing `examples/` profile is
  fictional and safe to extend.
- Prefer deterministic checks over "the model said it is fine" whenever possible.

## Good first contributions

- Improve documentation for first-time users.
- Add synthetic job descriptions or toy profile cases.
- Improve QA checks in `tools/qa_one_job.py`.
- Add more role-family base examples under `family_bases/`.
- Make setup easier without weakening the privacy or truthfulness rules.

## Local checks

Before opening a pull request, run:

```bash
pip install -r requirements-dev.txt
python3 tools/redact_scan.py
pytest -q
python3 -m py_compile tools/*.py
```

The privacy scan must be clean. If it reports a real email, phone number, home
path, key, or other private detail, remove the data rather than suppressing the
check.

## Pull request checklist

- The change keeps personal data out of the repository.
- Any examples or fixtures are synthetic.
- The README or relevant guide is updated when behavior changes.
- The local checks above pass.

Small, focused pull requests are easiest to review.
