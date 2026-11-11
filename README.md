# vulnerable-app-remediation

Fixing real scanner findings in a deliberately vulnerable Python app, taking a GitHub Actions security pipeline from red to green.

> **Warning:** `app.py` is a training example written with security flaws in its first version. Do not deploy it.

## What this project shows

1. A small Flask app with common vulnerabilities (SQL injection, command injection, unsafe YAML loading, outdated dependencies).
2. A pipeline that scans it with Gitleaks, Semgrep, and Trivy, and fails the build on findings (a security gate).
3. The first run fails. I read each finding, fixed the code, and re-ran the pipeline until it passed.

## Results

| Scanner | What it checks | Before | After |
|---|---|---|---|
| Gitleaks | Hardcoded secrets in the repo | 0 | 0 |
| Semgrep | Insecure code and workflow patterns | 17 findings | 0 |
| Trivy | Vulnerable packages and misconfigurations | 4 findings (1 critical, 3 high) | 0 |

## Before: the gate blocks the build 

<img width="736" height="598" alt="Screenshot 2026-11-11 124241" src="https://github.com/user-attachments/assets/da9afe99-0fa6-436c-895b-87275052ab2e" />


## After: all checks pass 

<img width="742" height="616" alt="image" src="https://github.com/user-attachments/assets/e8989df7-be64-4dd3-adda-2d34688d3fdd" />


## Fixes

### Dependencies (Trivy)

| Package | Vulnerability | Severity | Old version | New version |
|---|---|---|---|---|
| PyYAML | CVE-2020-14343 | Critical | 5.3.1 | 6.0.2 |
| Flask | CVE-2023-30861 | High | 1.0.2 | 3.0.3 |
| Jinja2 | CVE-2019-10906 | High | 2.10 | 3.1.6 |
| requests | CVE-2018-18074 | High | 2.19.0 | 2.32.4 |

I upgraded past the minimum fixed versions that Trivy listed, because older fixed releases have newer known vulnerabilities.

### Application code (Semgrep)

| Issue | Fix |
|---|---|
| SQL injection from string-formatted query | Parameterized query with a `?` placeholder |
| Command injection from `shell=True` and user input | No shell, a list of arguments, and a strict host-name pattern |
| Unsafe deserialization with `yaml.load` | `yaml.safe_load` |
| Hardcoded secret key | Read from the `SECRET_KEY` environment variable |
| Flask debug mode on | Debug turned off |
| Server bound to all interfaces (`0.0.0.0`) | Bound to `127.0.0.1` |

### Pipeline and container hardening

| Issue | Fix |
|---|---|
| Mutable action tags (`@v4`, `@v2`), flagged by Semgrep | Pinned every action to a full commit SHA |
| Container ran as root | Added a non-root user in the Dockerfile |

## How the pipeline works

- Gitleaks scans the repo and its history for secrets.
- Semgrep scans the code and workflow files and fails on any finding.
- Trivy scans dependencies, secrets, and misconfigurations and fails on HIGH or CRITICAL findings.

## Limitations

- The scanners analyze files, not the running application, so nothing here replaces dynamic testing.
- Trivy checks the packages listed in `requirements.txt`, not indirect dependencies.
- I did not write automated tests for the app's behavior, so the fixes are checked by the scanners only.
- The scanner Docker images (`semgrep/semgrep`, `aquasec/trivy:latest`) are not pinned by digest.
