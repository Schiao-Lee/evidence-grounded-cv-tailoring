# Security Policy

This project is local-first and intentionally handles sensitive personal data:
CVs, contact details, job applications, and interview preparation notes.

## Supported versions

This is a working prototype. Security fixes should target the `main` branch.

## Reporting a vulnerability

Please do not open a public issue for vulnerabilities, leaked personal data, or
anything that could expose a user's private CV or job-search information.

Use GitHub's private vulnerability reporting / Security Advisory flow if it is
available for this repository. If that is not available, contact the maintainer
through their GitHub profile and include only the minimum detail needed to
understand the issue.

## Data handling expectations

- Do not attach real CVs, real job applications, or private contact details to
  issues or pull requests.
- Use synthetic data in examples, tests, and screenshots.
- Run `python3 tools/redact_scan.py` before publishing changes.
- Treat generated PDFs and job folders as private by default.

## Scope

Useful reports include:

- A path where private data could be committed accidentally.
- A redaction scanner bypass.
- A workflow step that encourages or permits unsupported CV claims.
- A dependency or script behavior that exposes local user data.
