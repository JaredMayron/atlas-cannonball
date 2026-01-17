---
description: Scan Python dependencies for known vulnerabilities using pip-audit
---

// turbo-all

# Pip-Audit Dependency Scan

This workflow scans Python dependencies for known security vulnerabilities using a virtual environment.

## Steps

1. Run pip-audit using uv:

```bash
cd GCP && uv run pip-audit
```

## Interpreting Results

- **No vulnerabilities found**: Dependencies are up to date with no known security issues
- **Vulnerabilities found**: Update affected packages to the recommended fixed versions
- **No fix available**: Consider finding alternative packages or implementing additional security controls
