---
name: cloudflare-tunnel
description: "Cloudflare Tunnel management — temporary (trycloudflare) and fixed (Zero Trust named) tunnels. Covers setup, DNS routing, config persistence, and avoiding URL-change-on-restart pitfalls."
tags: [cloudflare, tunnel, networking, deploy, public-access]
triggers:
  - cloudflare tunnel
  - 隧道配置
  - 固定域名
  - trycloudflare
  - 公网访问
  - tunnel URL changed
---

# Cloudflare Tunnel Management

## When to Use
- Setting up public access for a backend/web service
- Migrating from temporary tunnel to fixed domain
- Troubleshooting tunnel connectivity issues
- Avoiding APK rebuilds due to URL changes

## Two Tunnel Modes

| Mode | URL | Persistence | Use Case |
|------|-----|-------------|----------|
| **trycloudflare** | `xxx-xxx-xxx.trycloudflare.com` | ❌ Changes on restart | Quick testing, dev |
| **Zero Trust named** | `your-domain.example.com` | ✅ Fixed forever | Production, APK hardcoding |

## ⚠️ CRITICAL: trycloudflare URL Changes on Every Restart

**Root cause of repeated APK rebuilds**: using trycloudflare temporary tunnels and hardcoding URLs into APKs. Every tunnel restart = new URL = APK must be rebuilt.

**Solution**: For any service that APKs connect to, use a **fixed named tunnel** instead.

## Mode 1: Temporary Tunnel (trycloudflare)

### Quick Start
```bash
# Start tunnel pointing to local service
nohup cloudflared tunnel --url http://localhost:3002 > /tmp/cf-tunnel.log 2>&1 &

# Get the URL (wait 5s for it to appear)
sleep 5 && grep -oP 'https://[^ ]+trycloudflare.com' /tmp/cf-tunnel.log | tail -1
```

### Pitfalls
- URL changes EVERY restart — never hardcode in production
- Multiple `cloudflared` processes can conflict — kill all first: `pkill -f cloudflared`
- No authentication — anyone with the URL can access

## Mode 2: Fixed Named Tunnel (Zero Trust)

### Prerequisites
1. Cloudflare account with Zero Trust enabled (free tier: 1 user)
2. A domain managed by Cloudflare DNS (or add one)
3. `cloudflared` installed on the server

### Setup (One-Time)
```bash
# 1. Login to Cloudflare (opens browser, saves cert)
cloudflared tunnel login

# 2. Create a named tunnel
cloudflared tunnel create my-app

# 3. Note the Tunnel ID (shown after creation)
# Example: 1234abcd-5678-efgh-9012-ijklmnopqrst

# 4. Create config file
mkdir -p ~/.cloudflared
cat > ~/.cloudflared/config.yml << 'EOF'
tunnel: my-app
credentials-file: /home/test/.cloudflared/1234abcd-5678-efgh-9012-ijklmnopqrst.json

ingress:
  - hostname: app.example.com
    service: http://localhost:3002
  - hostname: api.example.com
    service: http://localhost:8686
  - service: http_status:404
EOF

# 5. Add DNS records (one per hostname)
cloudflared tunnel route dns my-app app.example.com
cloudflared tunnel route dns my-app api.example.com

# 6. Run the tunnel
cloudflared tunnel run my-app
```

### Run as System Service (survives reboot)
```bash
# Install as systemd service
sudo cloudflared service install
sudo systemctl enable cloudflared
sudo systemctl start cloudflared

# Or user-level (no sudo):
cp ~/.cloudflared/config.yml ~/.config/cloudflared/config.yml
nohup cloudflared tunnel run my-app > /tmp/cf-named-tunnel.log 2>&1 &
```

### Benefits
- **Fixed URL** — never changes, APKs can hardcode it
- **Custom domain** — `api.ridehermes.com` instead of `xxx.trycloudflare.com`
- **TLS managed** — Cloudflare handles certificates
- **No port exposure** — no need to open firewall ports

## Migration: trycloudflare → Named Tunnel

```bash
# 1. Set up named tunnel (see Mode 2 above)
# 2. Start named tunnel alongside temporary one
# 3. Rebuild APKs ONCE with the fixed URL:
flutter build apk --release \
  --dart-define=API_BASE_URL=https://api.example.com \
  --dart-define=WS_URL=wss://api.example.com/ws/location
# 4. Kill temporary tunnel
pkill -f "cloudflared tunnel --url"
# 5. Done — never rebuild APKs for URL changes again
```

## Tunnel Health Monitoring

```bash
# Check tunnel is alive
ps aux | grep cloudflared | grep -v grep

# Check tunnel logs for errors
tail -20 /tmp/cf-tunnel.log

# Test connectivity
curl -s -o /dev/null -w '%{http_code}' https://your-tunnel-url.com/health
```

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| URL changed after reboot | Using trycloudflare | Migrate to named tunnel |
| `connection refused` | Tunnel pointing to wrong port | Check `--url` or config.yml ingress |
| `ERR_TOO_MANY_REDIRECTS` | Tunnel + app both doing HTTPS redirect | Use `http://localhost:PORT` in tunnel config |
| Multiple tunnels conflict | Old cloudflared still running | `pkill -f cloudflared` then restart |
| Named tunnel auth expired | `cloudflared tunnel login` cert expired | Re-run `cloudflared tunnel login` |

## Cost Reference

| Feature | Free Tier | Paid ($5/mo) |
|---------|-----------|--------------|
| Tunnels | 1 | Unlimited |
| Users | 1 (yourself) | Up to 50 |
| Bandwidth | Unlimited | Unlimited |
| Custom domains | ✅ | ✅ |
| SSO/Auth | ❌ | ✅ |

For single-user dev/prod, free tier is sufficient.
