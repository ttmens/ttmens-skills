# Cloud Vendor API Migration Patterns

When migrating from managed cloud services (WeChat Cloud Hosting, Vercel Edge, etc.) to self-hosted ECS/VPS, the frontend API client usually needs a complete rewrite — not just a URL change.

## WeChat Cloud Hosting → ECS (HTTP Direct)

### Before (wx.cloud.callContainer)
```typescript
// Taro/WeChat mini-program calling cloud hosting
wx.cloud.callContainer({
  config: { env: 'prod-xxxx' },
  path: '/api/naming/generate',
  method: 'POST',
  header: {
    'X-WX-SERVICE': 'express-isyu',
    'content-type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  data: requestData,
  timeout: 30000,
  success: (res) => resolve(res.data),
  fail: (err) => reject(err)
})
```

### After (Taro.request to ECS)
```typescript
// Direct HTTP to ECS server
const res = await Taro.request({
  url: `http://39.97.254.161/api/naming/generate`,
  method: 'POST',
  data: requestData,
  timeout: 30000,
  header: {
    'content-type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
  }
})
if (res.statusCode >= 400) throw new Error(res.data?.error)
return res.data
```

### Key Differences
| Aspect | Cloud Hosting | ECS Direct |
|--------|--------------|------------|
| Auth | Implicit (wx.cloud.init) | Manual JWT in header |
| Routing | `X-WX-SERVICE` header + path | Full URL with host |
| DNS | No domain needed | Need IP or domain |
| HTTPS | Automatic | Need cert (Let's Encrypt) |
| WeChat domain whitelist | Not needed | Must add to whitelist |
| Timeout handling | Built-in retry | Manual |

### Migration Checklist
1. **Replace API client**: `callContainer()` → `Taro.request()` or `fetch()`
2. **Update base URL**: Cloud env ID → ECS IP/domain
3. **Remove cloud init**: Delete `wx.cloud.init()` from app startup
4. **Add domain whitelist**: WeChat MP console → Development → Server domains
5. **HTTPS for production**: WeChat requires HTTPS for official releases
6. **Test all endpoints**: Cloud hosting may have different path conventions

### WeChat Mini-Program Domain Whitelist
In WeChat MP Console → Development Management → Development Settings → Server Domains:
- **request合法域名**: `https://your-domain.com` (or `http://IP` for dev only)
- **uploadFile合法域名**: If using file uploads
- **downloadFile合法域名**: If downloading files

**Dev mode bypass**: Enable "不校验合法域名" in WeChat DevTools settings for testing.

## General Pattern: Managed Service → Self-Hosted

When migrating from any managed service to self-hosted:

1. **Identify vendor-specific APIs**: `wx.cloud.*`, `vercel/edge`, `aws-sdk` calls
2. **Map to standard HTTP**: Most managed services have HTTP equivalents
3. **Handle auth migration**: Cloud services often have implicit auth; self-hosted needs explicit tokens
4. **Update CORS**: Managed services handle CORS automatically; self-hosted needs explicit config
5. **SSL/TLS**: Managed = automatic; self-hosted = Let's Encrypt or similar
6. **DNS**: Update frontend config to point to new host

### Anti-Pattern: Mechanical Replication
**DON'T**: Try to replicate the managed service architecture on bare metal.
- Cloud Hosting container routing → Just use nginx reverse proxy
- Edge functions → Regular Node.js server
- Managed DB connection strings → Local DB with standard connection

**DO**: Rethink the architecture for the new environment. The user signal is "换到XX部署 很多技术实现可以重新审视" — this means optimize for the new target, not preserve the old approach.
