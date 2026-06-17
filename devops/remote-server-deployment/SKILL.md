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

Deploy full-stack applications (Node.js/TypeScript monorepos, Docker-based stacks) to remote Linux servers via SSH, handling common permission and environment constraints.

## Pre-Flight Checklist

**STEP ZERO: Validate SSH Access AND Project State FIRST**

```bash
# 1. Test SSH with credentials
ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no -p $PORT $USER@$HOST "echo SSH_OK"

# 2. Check sudo access EARLY (gates many decisions)
ssh $USER@$HOST "sudo -n whoami 2>/dev/null && echo 'PASSWORDLESS_SUDO' || echo 'NEEDS_PASSWORD'"

# 3. Check existing services
ssh $USER@$HOST "which docker node pnpm psql redis-cli 2>/dev/null; pm2 list 2>/dev/null"

# 4. Check system resources
ssh $USER@$HOST "free -h | head -2; df -h / | tail -1; nproc"

# 5. Validate project state
ssh $USER@$HOST "cd /path/to/project && git log --oneline -5 && pm2 list"
```

**When SSH fails**:
- Password auth fails → credentials changed, ask user
- SSH key fails → key removed, ask user to re-install via cloud console VNC
- Both fail → server down or firewall changed

**Critical**: Do NOT fall back to browser-based verification. Without SSH access, you are blocked.

### SSH Key Setup (FIRST on Any New Server)

```bash
# Generate key locally (if not exists)
ssh-keygen -t ed25519 -f ~/.ssh/deploy_key -N ""

# On FIRST connection, immediately install the key
ssh $USER@$HOST "mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo '$(cat ~/.ssh/deploy_key.pub)' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"

# Verify key auth works
ssh -i ~/.ssh/deploy_key -o PasswordAuthentication=no $USER@$HOST "echo KEY_OK"
```

**NEVER**: Make more than 3 password-auth SSH connections in quick succession (triggers fail2ban).

### Recovery: When You Get Locked Out

User must use cloud console VNC to:
```bash
fail2ban-client set sshd unbanip <agent-public-ip>
# OR
systemctl restart sshd
```

## Installation Strategies

### Node.js Without Sudo (nvm)

```bash
ssh $USER@$HOST 'curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash'
ssh $USER@$HOST 'export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && nvm install 20 && npm install -g pnpm'
```

**Pitfall**: Every subsequent SSH command needs the nvm sourcing prefix:
```bash
'export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && YOUR_COMMAND'
```

## Database Options

See `references/database-fallback.md` for the full decision tree and fallback hierarchy.

Quick summary:
1. External DB service (Supabase/Neon/Railway) — best for no-sudo scenarios
2. SQLite (modify Prisma schema) — good for demos/MVP
3. Manual install script — user runs with their password

## Deployment Workflow

1. **Pre-flight** (5 min): Run all checks above
2. **Transfer code**: `tar` + `scp` (exclude node_modules, .next, dist)
3. **Install deps**: `pnpm install` on server
4. **Build**: `pnpm build` on server (see Monorepo Build Order below)
5. **Configure**: Set up `.env` with correct values
6. **Database**: Apply migration strategy from decision tree
7. **Start**: Use `pm2` for process management
8. **Verify**: Health check endpoints + **browser E2E verification**

### Monorepo Build Order (TypeScript/pnpm)

```bash
# 1. Database schema first (generates Prisma client)
pnpm --filter @org/db exec prisma generate

# 2. Shared libraries / engines
pnpm --filter @org/engine build

# 3. API server
pnpm --filter @org/api build

# 4. Frontend last
pnpm --filter @org/web build
```

## Process Management

### PM2 Ecosystem Config (Recommended)

```javascript
module.exports = {
  apps: [
    {
      name: "api",
      script: "./packages/api/dist/index.js",
      cwd: "/home/user/project",
      instances: 1,
      autorestart: true,
      env: { NODE_ENV: "production", API_PORT: 3001 }
    },
    {
      name: "web",
      script: "node_modules/next/dist/bin/next",
      args: "start -p 3000",
      cwd: "/home/user/project/packages/web",
      env: { NODE_ENV: "production" }
    }
  ]
};
```

```bash
scp ecosystem.config.js user@host:~/project/
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

### Next.js Standalone Mode

If `next.config.js` has `output: 'standalone'`:
- PM2 must point to standalone server.js, NOT `next start`
- Must manually copy static files: `cp -r .next/static .next/standalone/.next/`
- `rewrites` do NOT work in standalone mode — use nginx or standard `next start` instead

## Post-Deploy Verification

**Browser E2E verification is mandatory** — curl 200 ≠ app works.

1. Navigate to login page → confirm styles render
2. Login → confirm redirect to homepage
3. Check 2-3 core pages → no white screen, no JS errors
4. Check `localStorage.getItem('token')` → confirm auth works

## Reference Files

| File | Contents |
|------|----------|
| `references/deployment-pitfalls.md` | PM2, Next.js, SSH, transfer, database, Cloudflare pitfalls |
| `references/platform-specific.md` | Windows agent, fresh ECS, nginx, paramiko |
| `references/database-fallback.md` | Database decision tree, external DB, SQLite, manual install |
