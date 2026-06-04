# Security Policy

## Supported Versions

StudyMate CLI is early-stage software. Security fixes are applied to the current
`main` branch and the latest published release, if one exists.

| Version | Supported |
| ------- | --------- |
| latest  | Yes       |

## Reporting a Vulnerability

Please do not open a public issue for a suspected security vulnerability.

Report vulnerabilities by using GitHub's private vulnerability reporting flow, if
available for this repository, or by contacting the repository owner through
GitHub with enough detail to reproduce the issue.

Helpful details include:

- the affected command or workflow
- the operating system and Python version
- a minimal input file or command that demonstrates the problem
- whether private files, credentials, or network access are involved
- any suggested mitigation, if known

## What to Expect

The maintainer will aim to acknowledge a report within 7 days. If the issue is
confirmed, the maintainer will coordinate a fix and publish a security advisory
or release notes when appropriate.

## Project Security Model

StudyMate is local-first. It should not upload notes, deadlines, thesis files, or
review state by default. Features that access the network, such as link checking,
must be explicit and documented.

Security-sensitive changes should preserve these expectations:

- student files remain local unless the user explicitly chooses otherwise
- commands should fail safely when files or config are missing
- machine-readable output should not leak unrelated environment details
- CI integrations should avoid printing secrets or private document content
