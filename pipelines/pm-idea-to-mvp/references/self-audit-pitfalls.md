# Self-Audit Pitfalls & Patterns (from v6.2 → v6.2.1)

> Lessons learned from the first comprehensive self-audit of all 22+ pipeline scripts.
> Use this as a checklist when running future audits to avoid rediscovering these issues.

## Python Gotchas Found

### 1. subprocess.run timeout parameter ordering

**Bug**: `subprocess.run(timeout=60, ["git", "push", ...])` → SyntaxError
**Fix**: `subprocess.run(["git", "push", ...], timeout=60)` — keyword args must come AFTER positional args.

**Audit check**: `grep -n "timeout=" scripts/*.py | grep -v "timeout=[0-9]*$"` — any timeout before a list literal is broken.

### 2. read_file output corruption when writing back

**Bug**: `read_file` returns lines prefixed with `N|content`. If you use that output to `write_file`, the target gets corrupted with `1|`, `2|` prefixes.
**Fix**: Always use `open(path).read()` in execute_code for read-modify-write cycles, not `read_file` from hermes_tools.

**Audit check**: If a .py file starts with `1|#!/usr/bin/env`, it was corrupted by this pattern.

### 3. Regex replacement creating nested quotes

**Bug**: Replacing a string literal with code containing quotes can create broken syntax like `Path(r"str(Path(...)")`.
**Fix**: When doing regex replacements on Python source, verify the result compiles (`python -m py_compile`) immediately after each replacement.

### 4. check_docs_ssot.py false positive on multi-tech consistency

**Bug**: Flagged "conflict" when all docs consistently mentioned both SQLite AND PostgreSQL (correct state).
**Fix**: Only flag when docs have genuinely different single-tech claims, not when all docs agree on a multi-tech stack.

## Version Drift Pattern

**Finding**: After updating 3 core scripts to v6.2.0, the other 9 still reported 6.0.0/6.1.0.
**Prevention**: After any version bump, run: `grep -r "PIPELINE_VERSION" scripts/*.py` and verify all match SKILL.md frontmatter.

## Hardcoded Path Pattern

**Finding**: 5 scripts had `D:/workspace/` or `D:\hermes-data\` hardcoded. These break on any non-Windows or different-username machine.
**Prevention**: `grep -rn "D:/\|D:\\\\" scripts/*.py` — any match is a bug. Use `Path(__file__).resolve().parents[N]` instead.

## Feedback Loop Gap

**Finding**: `feedback.jsonl` was written by inner-loop-driver.py but never read by any script. The "self-evolution闭环" was broken.
**Fix**: Added `consume-feedback.py` to parse, summarize, and mark feedback as consumed during retro stage.
**Audit check**: For any .jsonl file written by one script, verify at least one other script reads it.

## Missing --all-stages Pattern

**Finding**: `validate-gates.py` only validated one stage at a time. Full pipeline audit required 10 separate invocations.
**Fix**: Added `--all-stages` flag that iterates all stages and produces a unified JSON report.
**Lesson**: Any per-entity validation script should have a `--all` mode for batch verification.

## Quick Audit Commands

```bash
# Syntax check all scripts
for f in scripts/*.py; do python -m py_compile "$f" 2>&1 && echo "✅ $f" || echo "❌ $f"; done

# Version consistency
grep -oP 'PIPELINE_VERSION\s*=\s*"\K[^"]+' scripts/*.py | sort -u

# Hardcoded paths
grep -rn "D:/\|D:\\\\" scripts/*.py

# subprocess timeout ordering
grep -n "subprocess.run(timeout=" scripts/*.py
grep -n "subprocess.check_output(timeout=" scripts/*.py

# Write-only files (created but never read)
grep -rl "feedback.jsonl" scripts/*.py  # check if any script reads it
```

---

*Generated from v6.2 → v6.2.1 self-audit session, 2026-06-13*
