# Browser tools SSOT (multi-agent)

Agents on **Cursor**, **Hermes**, and **OpenCode** use different browser tool names. Use **intent** below — map to your platform's available tools.

## Intent mapping

| Intent | Cursor MCP (cursor-ide-browser) | Hermes / dogfood alias | Minimum evidence |
|--------|--------------------------------|------------------------|------------------|
| Navigate | `browser_navigate` | same | URL loaded |
| Page structure | `browser_snapshot` | DOM / accessibility snapshot | a11y tree or refs |
| Screenshot | `browser_take_screenshot` | `browser_vision` | file path saved |
| Console errors | `browser_cdp` (Runtime/Log) | `browser_console` | no uncaught errors after action |
| Click | `browser_click` | same | element ref or text |
| Type / fill | `browser_type`, `browser_fill` | same | input updated |
| Scroll | `browser_scroll` | same | below-fold visible |
| Keyboard | `browser_press_key` | `browser_press` | focus moves / submit |

Reference: [`dogfood`](../../../domains/qa/dogfood/SKILL.md) 5-phase workflow.

## Ship / MVP browser E2E checklist (v7.1)

After deploy or local `pnpm dev`:

1. **Navigate** to public or local URL
2. **Snapshot** — confirm main nav / hero / primary CTA present
3. **Screenshot** — save to `docs/ui-snapshots/post.png`
4. **Console** — no red errors on load + after primary flow
5. **Walk 1 core journey** from `03b-user-journey.md` (click through)
6. Run `python {SKILLS_ROOT}/scripts/ui_acceptance.py --full --project-root {PROJECT_ROOT}`

**Anti-rationalization:** `curl 200` ≠ UI works. Spinner-only body = failed.

## Cursor lock workflow

```
browser_navigate → browser_lock → (interactions) → browser_unlock
```

Do not call `browser_lock` before `browser_navigate` on a new tab.

## Hermes notes

Hermes workers may use different browser MCP bundles. If `browser_vision` unavailable, use snapshot + screenshot equivalents from your runtime docs.
