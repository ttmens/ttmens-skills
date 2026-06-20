---
name: remote-server-deployment
description: Deploy full-stack apps to remote Linux servers via SSH. Covers pre-flight checks, dependency installation strategies, database options under permission constraints, and fallback hierarchies.
triggers:
  - deploy to remote server
  - deploy to VPS
  - SSH deployment
  - remote server setup
  - production deployment
---

# Remote Server Deployment

Deploy full-stack applications (Node.js/TypeScript monorepos, Docker-based stacks) to remote Linux servers via SSH.

**SSOT**: [docs/DEPLOY_CONVENTIONS.md](../../docs/DEPLOY_CONVENTIONS.md) — registry, project deploy.yaml, .env secrets.

## Project State Recovery

**CRITICAL: Always start from deploy-servers.yaml, NEVER from session context.**

1. **Read deploy config FIRST**: `cat $HERMES_HOME/config/deploy-servers.yaml` → `default_server` and all entries
2. **SSH to DEFAULT server** and search: `find ~ -maxdepth 3 -name '<project-name>' -type d`
3. **Verify state**: `ss -tlnp`, `pm2 list`
4. **Cross-reference** ports and health_urls from project `deploy.yaml`

**Pitfall**: `dc1-priority` hosts most pm-* projects. Other servers are for specific services only.

## Pre-Flight Checklist

**STEP ZERO: Validate SSH Access**

Resolve `$HOST`, `$PORT`, `$USER`, `$KEY` from registry + project `deploy.yaml`:

```bash
# Key-first (from deploy-servers.yaml key_path)
ssh -i ~/.ssh/id_ed25519_deploy -o ConnectTimeout=10 -p $PORT $USER@$HOST "echo SSH_OK"

# Check sudo
ssh -i $KEY -p $PORT $USER@$HOST "sudo -n whoami 2>/dev/null && echo PASSWORDLESS_SUDO || echo NEEDS_PASSWORD"

# Check services
ssh -i $KEY -p $PORT $USER@$HOST "which docker node pnpm 2>/dev/null; pm2 list 2>/dev/null"
```

**When SSH fails**: ask user — do not guess credentials from session history.

### SSH Key Setup

```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_deploy -N ""
ssh -i ~/.ssh/id_ed25519_deploy -o PasswordAuthentication=no -p $PORT $USER@$HOST "echo KEY_OK"
```

**NEVER**: more than 3 rapid password-auth SSH attempts (fail2ban).

## No-Sudo Stack

See `references/no-sudo-stack.md` and `references/flutter-android-sdk-setup.md`.

## Database Options

See `references/database-fallback.md`.

## Deployment Workflow

1. Pre-flight (registry + SSH)
2. `git clone` / `git pull` on server
3. `pnpm install` + build (monorepo order: db → libs → api → web)
4. Configure `.env` on server
5. `pm2 start` / restart
6. **Browser E2E verification** (mandatory for ship gate)

## Reference Files

| File | Contents |
|------|----------|
| `references/no-sudo-stack.md` | User-level full stack without sudo |
| `references/flutter-android-sdk-setup.md` | Flutter + Android SDK user install |
| `references/deployment-pitfalls.md` | PM2, Next.js, SSH pitfalls |
| `references/platform-specific.md` | Windows agent, paramiko |
| `references/database-fallback.md` | DB decision tree |
