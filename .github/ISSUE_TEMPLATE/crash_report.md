---
name: Crash report
about: Create an issue for cases causing checkov to crash
title: ''
labels: 'crash'
assignees: ''

---

**Describe the issue**
Explain what you expected to happen when checkov crashed.

**Examples**
Please share an example code sample (in the IaC of your choice) + the expected outcomes.

**Exception Trace**
Please share the trace for the exception and all relevant output by checkov.
To maximize the understanding, please run checkov with LOG_LEVEL set to debug
as follows:
```sh
LOG_LEVEL=DEBUG checkov ...
```

**Desktop (please complete the following information):**
 - OS: [e.g. iOS]
 - Checkov Version [e.g. 22]

**Additional context**
Add any other context about the problem here (e.g. code snippets).
