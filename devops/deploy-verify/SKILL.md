---
name: deploy-verify
description: "Post-deployment automated verification — health checks, port reachability, API smoke tests, browser E2E. Use after every deploy/ship to catch failures immediately."
tags: [deploy, verify, health-check, smoke-test, post-deploy]
triggers:
  - 部署后验证
  - deploy verify
  - 服务是否正常
  - 部署检查
  - post-deploy check
---

# Deploy Verify — 部署后自动验证

## When to Use
- After deploying any service (web, API, backend)
- After restarting tunnels or changing ports
- After APK rebuild with new backend URLs
- As part of ship gate (mandatory before marking deploy complete)

## ⚠️ CRITICAL: Never Skip Post-Deploy Verification

**Root cause of "deployed but unreachable" failures**: deploying services without verifying they're actually accessible. Discovery of failures is delayed until user tries to use the service.

**Rule**: Every deploy MUST be followed by verification within the SAME turn. If verification fails, fix immediately — don't report "deployed" and discover issues later.

## Verification Checklist (execute in order)

### Level 1: Process Alive (5 seconds)
```bash
# Check process is running
ssh $SERVER "ps aux | grep -E '$PROCESS_NAME' | grep -v grep"
# Check port is listening
ssh $SERVER "ss -tlnp | grep :$PORT"
```

### Level 2: Local Reachability (10 seconds)
```bash
# localhost check from server
ssh $SERVER "curl -s -o /dev/null -w '%{http_code}' http://localhost:$PORT/health"
# Expected: 200
```

### Level 3: Public Reachability (15 seconds)
```bash
# Via tunnel/public URL
curl -s -o /dev/null -w '%{http_code}' "$PUBLIC_URL/health"
# Expected: 200

# If tunnel: verify tunnel process is alive
ssh $SERVER "ps aux | grep cloudflared | grep -v grep"
```

### Level 4: API Smoke Test (20 seconds)
```bash
# Test a real API endpoint (not just health)
curl -s "$PUBLIC_URL/api/v1/auth/login-or-register" \
  -X POST -H "Content-Type: application/json" \
  -d '{"phone":"13800138000","password":"admin123"}' | head -c 200
# Expected: JSON response with token/user data
```

### Level 5: Browser E2E (30 seconds, for web apps)
```
# Open in browser and verify:
# 1. Page loads (not 502/504)
# 2. Login form is visible
# 3. Can submit login
# 4. Dashboard renders
```

## Verification Matrix by Service Type

| Service | L1 | L2 | L3 | L4 | L5 | Min Required |
|---------|----|----|----|----|----|--------------|
| Go API | ✅ | ✅ | ✅ | ✅ | — | L3 |
| Web Frontend | ✅ | ✅ | ✅ | — | ✅ | L5 |
| Flutter Backend | ✅ | ✅ | ✅ | ✅ | — | L4 |
| Redis/DB | ✅ | ✅ | — | — | — | L2 |
| WebSocket | ✅ | ✅ | ✅ | ✅* | — | L3 + WS handshake |

*WS smoke test: `curl -H "Upgrade: websocket" -H "Connection: Upgrade" $WS_URL`

## Tunnel-Specific Verification

After starting/restarting a Cloudflare tunnel:
```bash
# 1. Get the tunnel URL
TUNNEL_URL=$(ssh $SERVER "grep 'trycloudflare.com' /tmp/cf-tunnel.log | tail -1" | grep -oP 'https://[^ ]+')

# 2. Verify it responds
curl -s -o /dev/null -w '%{http_code}' "$TUNNEL_URL/"

# 3. If using trycloudflare: URL changes on restart → MUST rebuild APKs
echo "⚠️ Tunnel URL changed. APKs hardcoded with old URL will NOT connect."
echo "   Rebuild: flutter build apk --dart-define=API_BASE_URL=$TUNNEL_URL"
```

## Common Failure Patterns

| Symptom | Root Cause | Fix |
|---------|------------|-----|
| L2 OK, L3 FAIL | Tunnel not running / wrong port mapping | Restart cloudflared with correct `--url` |
| L3 OK, L4 FAIL | Backend crashed after tunnel started | Check backend logs, restart |
| L4 OK, L5 FAIL | Frontend JS error / CORS issue | Browser console check |
| All OK but APK fails | APK hardcoded with old tunnel URL | Rebuild with `--dart-define` |
| L1 FAIL | Process not started / crashed | Check logs, restart |

## Automation Template

```bash
#!/bin/bash
# deploy-verify.sh — run after every deploy
set -e
SERVER=${1:-dc1-priority}
PORTS=${2:-"8686 3002 6379"}

echo "=== Deploy Verification ==="
for PORT in $PORTS; do
  STATUS=$(ssh $SERVER "curl -s -o /dev/null -w '%{http_code}' http://localhost:$PORT/ 2>/dev/null || echo '000'")
  if [ "$STATUS" = "200" ] || [ "$STATUS" = "301" ] || [ "$STATUS" = "302" ]; then
    echo "✅ Port $PORT: HTTP $STATUS"
  else
    echo "❌ Port $PORT: HTTP $STATUS — NEEDS ATTENTION"
  fi
done

# Tunnel check
TUNNEL=$(ssh $SERVER "pgrep -f cloudflared" 2>/dev/null)
if [ -n "$TUNNEL" ]; then
  URL=$(ssh $SERVER "grep 'trycloudflare.com' /tmp/cf-tunnel.log 2>/dev/null | tail -1" | grep -oP 'https://[^ ]+')
  PUBLIC_STATUS=$(curl -s -o /dev/null -w '%{http_code}' "$URL/" 2>/dev/null || echo "000")
  echo "✅ Tunnel: $URL (HTTP $PUBLIC_STATUS)"
else
  echo "❌ Tunnel: NOT RUNNING"
fi
```

## Pitfalls
- **trycloudflare URLs change on restart** — always verify tunnel URL hasn't changed
- **Backend may bind to 127.0.0.1** — tunnel must point to correct localhost port
- **Multiple cloudflared processes** — old ones may hijack the URL, kill all first
- **Firewall rules** — even if process is alive, port may not be externally reachable
- **APK URL mismatch** — the #1 post-deploy issue; always check `--dart-define` alignment
