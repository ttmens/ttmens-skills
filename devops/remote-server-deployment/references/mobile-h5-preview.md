# Mobile H5 Preview Template Pattern

Reusable pattern for building a standalone mobile-first HTML page served by the API server, for quick phone-based preview when the user can't access local dev tools.

## CSS Design Tokens (Chinese-style, warm palette)

```css
:root {
  --ink: #1A3A4A;        /* Primary text */
  --gold: #C9A96E;       /* Accent/highlight */
  --paper: #F8F5F0;      /* Background */
  --card: #FFFFFF;        /* Card surfaces */
  --good: #2D8C5A;       /* Success/high score */
  --bad: #C1453B;        /* Error/low score */
  --warn: #D4A017;       /* Warning/mid score */
}
body {
  font-family: -apple-system, 'PingFang SC', 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
  background: var(--paper);
  color: var(--ink);
  -webkit-font-smoothing: antialiased;
}
.container { max-width: 420px; margin: 0 auto; padding: 0 16px 80px; }
```

## Key Structural Patterns

### API Base URL (auto-adapts to any tunnel)
```javascript
const API_BASE = window.location.origin;
// Works with: https://abc123.trycloudflare.com, http://localhost:3101, etc.
```

### Loading Animation (step-by-step progress)
```javascript
const steps = ['step1','step2','step3','step4','step5'];
for (let i = 0; i < steps.length; i++) {
  await sleep(600);
  if (i > 0) {
    document.getElementById(steps[i-1]).className = 'done';
    document.getElementById(steps[i-1]).textContent = '✓ ' + label;
  }
  document.getElementById(steps[i]).className = 'active';
}
```

### POST JSON to API (same-origin, no CORS issues)
```javascript
const res = await fetch(`${API_BASE}/api/naming/generate`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(payload)
});
const data = await res.json();
```

### Score Color Coding
```javascript
const cls = val >= 80 ? 'high' : val >= 60 ? 'mid' : 'low';
// .high → green bg, .mid → yellow bg, .low → red bg
```

## Mobile UX Checklist

- [ ] Viewport meta: `<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">`
- [ ] Touch targets ≥ 44px (padding: 14px+ on buttons/inputs)
- [ ] Font size ≥ 16px on inputs (prevents iOS zoom)
- [ ] No horizontal scroll (max-width container + percentage widths)
- [ ] Loading state with visible progress (not just a spinner)
- [ ] Smooth scroll to top after results render
- [ ] Back button to return to form without page reload
- [ ] Error toast (fixed position, auto-dismiss after 3s)
- [ ] System font stack for native feel
- [ ] Card-based layout with subtle shadows (box-shadow: 0 2px 12px rgba(0,0,0,0.04))

## Fastify Static Plugin Registration Order

```typescript
// 1. CORS first (allows cross-origin if needed)
await fastify.register(cors, { origin: '*', credentials: true })

// 2. Static files (serves index.html at /)
await fastify.register(fastifyStatic, {
  root: path.join(__dirname, '..', 'public'),
  prefix: '/',
  decorateReply: true
})

// 3. API routes AFTER static (API paths take precedence over static)
await fastify.register(apiRoutes, { prefix: '/api' })
fastify.get('/health', ...)
```

**Why this order**: Fastify matches routes in registration order. If `/api/*` routes are registered before static, they work correctly. The static plugin serves `index.html` for any unmatched path under `/`, which is the desired fallback behavior for a single-page app.

## Template Sections

A typical mobile preview page has these sections:

1. **Header** — App name, tagline, social proof counter
2. **Form** — Input fields with labels, gender selector (tap cards), date/time pickers
3. **Optional fields** — Collapsible section (toggle visibility)
4. **Submit button** — Full-width, gradient background, disabled state during loading
5. **Loading overlay** — Fixed fullscreen, step-by-step progress, rotating quotes
6. **Results** — Back button, data cards, score tags, paywall section
7. **Error toast** — Fixed top-center, auto-dismiss

## When to Evolve Beyond This Pattern

- More than 3-4 pages → use proper routing (Taro H5 or Next.js)
- Need offline support → add service worker
- Need native features (camera, GPS) → must use mini-program or PWA
- Multiple users need different experiences → add auth + session management
- Performance matters → code-split, lazy-load, CDN for assets
