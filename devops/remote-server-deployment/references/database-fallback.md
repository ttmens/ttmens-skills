# Database Fallback Decision Tree

## Decision Tree

```
Has passwordless sudo?
├── YES → Install Docker + docker-compose → Use project's docker-compose.yml
└── NO → Has sudo with password?
    ├── YES → Try sudo with password (see pitfalls below)
    └── NO → Check for existing DB services
        ├── PostgreSQL exists → Use it directly
        └── Nothing exists → FALLBACK HIERARCHY:
            1. External DB service (Supabase/Neon/Railway free tier)
            2. SQLite (modify Prisma schema)
            3. Manual install script for user to run
```

## Fallback 1: External PostgreSQL Services

Best for maintaining original architecture without local DB:
- **Supabase**: Free tier, connection string provided
- **Neon**: Serverless Postgres, free tier
- **Railway**: $5 free credit/month

Just update `DATABASE_URL` in `.env`.

## Fallback 2: SQLite Quick Deploy

```prisma
datasource db {
  provider = "sqlite"
  url      = "file:./dev.db"
}
```

**Migration**: Use `npx prisma db push` (NOT `migrate dev` — requires interactive terminal).

**Full workflow**:
```bash
# 1. Update schema.prisma (change provider to sqlite)
# 2. Update .env: DATABASE_URL="file:./dev.db"
npx prisma db push
npx prisma generate
pnpm build
pm2 restart all
```

**Trade-offs**: No concurrent writes, no pgvector, limited JSON support. Good for demos/MVP.

## Fallback 3: Manual Install Script

```bash
#!/bin/bash
sudo apt-get update
sudo apt-get install -y postgresql redis-server
sudo systemctl enable postgresql redis-server
sudo systemctl start postgresql redis-server
```

## Exhaust Alternatives Before Fallback

Before presenting fallback options, try in order:

1. **Manual uidmap extraction** (for rootless Docker):
   ```bash
   cd /tmp && apt-get download uidmap
   mkdir -p ~/bin && dpkg-deb -x uidmap_*.deb uidmap_extracted
   cp uidmap_extracted/usr/bin/* ~/bin/
   ```

2. **Alternative Docker mirrors**: GitHub releases, Alibaba mirror, etc.

3. **Rootless container runtimes**: Check for podman, nerdctl, bubblewrap.

4. **Only after ALL above fail**: Present fallback options to user.

**User signal**: "没有别的方法吗？再想想" → you skipped this step.
