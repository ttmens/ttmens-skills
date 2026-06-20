# No-Sudo Full-Stack Deployment

> Reference for `remote-server-deployment` skill. See [DEPLOY_CONVENTIONS.md](../../docs/DEPLOY_CONVENTIONS.md).

When the remote user has **no passwordless sudo**, use user-level installs only.

## Stack Overview

| Component | Method | Path |
|-----------|--------|------|
| Node.js | nvm | `~/.nvm` |
| pnpm | npm global (user) | `~/.npm-global` |
| Go | wget + tar | `~/go/` |
| Redis | compile from source | `~/redis-stable/` |
| Database | SQLite (modify app) | project file |
| Static/API | Node.js server | PM2 |
| Public URL | cloudflared tunnel | `~/cloudflared` |
| Process manager | PM2 | user-level |

## Node.js (nvm)

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
export NVM_DIR="$HOME/.nvm" && . "$NVM_DIR/nvm.sh"
nvm install 20 && npm install -g pnpm pm2
```

Prefix every remote command with nvm sourcing when using nvm.

## SQLite Pivot

For MVP demos without managed DB:

1. Change Prisma `provider` to `sqlite` or use GORM sqlite driver
2. Run migrations locally or on server with file DB
3. Document in RUNBOOK.md

## cloudflared (no nginx)

```bash
~/cloudflared tunnel --url http://localhost:3000
```

Capture the `*.trycloudflare.com` URL for browser E2E verification.

## PM2 User-Level

```bash
pm2 start ecosystem.config.js
pm2 save
# pm2 startup may need sudo — skip if no sudo; use manual restart docs in RUNBOOK
```

## Principle

Do **not** ask for sudo password repeatedly. Pivot to this stack and document constraints in RUNBOOK.md.
