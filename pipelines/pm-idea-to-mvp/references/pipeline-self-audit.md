# Pipeline Self-Audit Methodology

> How to diagnose pipeline execution quality for any pm-{slug} project using the pipeline's own tools.

## When to Use

- Resuming work on an existing pm-{slug} project
- User asks "回顾一下这个项目" or "流水线执行得怎么样"
- Before starting a Refine cycle (understand what went wrong first)
- After a project ships (validate pipeline compliance)

## The 3-Layer Audit

### Layer 1: Artifact Inventory (what exists vs what should)

Check for v6.2 required artifacts:

```bash
# Governance artifacts (v6.2 mandatory)
for f in goals/align.yaml goals/research.yaml goals/analysis.yaml goals/spec.yaml goals/mvp.yaml goals/ship.yaml goals/retro.yaml PROGRESS.md harness-rules.yaml feedback.jsonl evolution-notes.md harness-improvements.md gates.json; do
  [ -f "$PROJECT_ROOT/$f" ] && echo "✅ $f" || echo "❌ $f"
done

# Check debates/ directory
ls -la "$PROJECT_ROOT/debates/" 2>/dev/null || echo "❌ debates/ missing"

# Stage artifacts
for f in 00-brief.md CONTEXT.md decisions.md 01-research.md 02-analysis.md 03-prd.md 03b-user-journey.md 05-retro.md 06-growth.md 07-ops-notes.md RUNBOOK.md; do
  [ -f "$PROJECT_ROOT/$f" ] && echo "✅ $f ($(wc -l < "$PROJECT_ROOT/$f") lines)" || echo "❌ $f"
done
```

### Layer 2: Automated Validation (run the pipeline's own tools)

```bash
# Run validate-gates for each completed stage
for stage in brief align research analysis spec mvp ship operate grow retro; do
  python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/validate-gates.py \
    --stage $stage --run $PROJECT_ROOT 2>/dev/null | \
    python -c "import sys,json; d=json.load(sys.stdin); print(f'$stage: {d[\"summary\"][\"passed\"]}/{d[\"summary\"][\"total\"]} passed')" 2>/dev/null || echo "$stage: ERROR"
done

# Run docs-hygiene (cross-document consistency)
python {SKILLS_ROOT}/scripts/check_docs_ssot.py --project-root $PROJECT_ROOT --json
```

### Layer 3: Quality Assessment (human judgment)

For each existing artifact, assess:
1. **Template-fill vs genuine analysis** — Does it contain project-specific insights or generic boilerplate?
2. **Internal consistency** — Do decisions.md, CONTEXT.md, and 02-analysis.md agree on tech stack?
3. **Completion honesty** — Are tasks marked [x] in openspec/tasks.md actually implemented?
4. **Depth adequacy** — Does CONTEXT.md have ≥50 lines of real analysis? Does 01-research.md have ≥5 URLs?

## Common Findings (from pm-knowledge-platform audit)

| Finding | Root Cause | v6.2 Fix |
|---------|-----------|----------|
| Tasks marked [x] but artifacts missing | No runtime verification | MANDATORY_RUNTIME_STAGES auto-enforcement |
| decisions.md says PostgreSQL, code uses SQLite | No cross-doc consistency check | check_docs_ssot.py tech-stack-conflict |
| debates/ directory missing | G1/G2 debate not enforced | validate-gates.py debate_required check |
| goals/ directory missing entirely | Goal primitives skipped | MANDATORY_GOAL_STAGES auto-enforcement |
| 04-mvp/ directory empty | MVP stage skipped file artifacts | goals_required check |
| Retro has no quantitative data | No section requirements | required_sections check |
| Operate/Grow stages skipped entirely | No artifacts required | 07-ops-notes.md required, min_lines raised |

## Quick Diagnostic Commands

```bash
# One-line: check if pipeline was actually run vs just documented
python {SKILLS_ROOT}/scripts/check_docs_ssot.py --project-root $PROJECT_ROOT --json | \
  python -c "import sys,json; d=json.load(sys.stdin); errors=[i for i in d.get('issues',[]) if i['severity']=='error']; print(f'ERRORS: {len(errors)}'); [print(f'  ❌ [{i[\"rule\"]}] {i[\"message\"]}') for i in errors]"

# Check if any pipeline scripts were ever run (look for gates.json timestamps)
cat $PROJECT_ROOT/gates.json 2>/dev/null | python -m json.tool | head -20

# Check inner loop execution (look for workflow_state.yaml)
cat $PROJECT_ROOT/docs/workflow_state.yaml 2>/dev/null || echo "❌ No inner loop state — MVP inner loop never ran"
```

## Output Format

Present findings as a structured report:

```
## Pipeline Execution Report: pm-{slug}

### Execution Rate: ~XX% (stages executed / total)

### Stage Status
| Stage | Artifacts | Quality | Gates |
|-------|-----------|---------|-------|
| brief | ✅ | ⭐⭐⭐⭐ | PASS |
| align | ⚠️ | ⭐⭐⭐ | FAIL (no debates/) |
| ...   | ... | ... | ... |

### Critical Issues
1. [P0] ...
2. [P0] ...

### Recommendations
1. ...
```

## Anti-Patterns Detected

1. **"Paper completion"** — All documents exist but are template-filled with no project-specific analysis
2. **"Ghost stages"** — Stage marked as passed in gates.json but required artifacts missing
3. **"Phantom features"** — Tasks marked [x] in openspec/tasks.md but code doesn't implement them
4. **"Silent skips"** — Stages with no artifacts and no gates.json entry (simply skipped)
5. **"Consistency drift"** — Different documents claim different tech stacks, deployment methods, or feature sets
