# Changelog

All notable changes to pm-idea-to-mvp pipeline will be documented in this file.

## [6.1.0] - 2026-06-13

### 🎯 Overview

**Production-tested version** with real-world deployment experience from 产品知识库平台 (pm-knowledge-platform) project.

### ✨ New Features

#### Knowledge Graph Visualization
- **New page**: `/graph` - Interactive knowledge graph visualization
- **Technology**: `react-force-graph-2d` for force-directed graph rendering
- **Features**:
  - Node color coding: BIZ_KL (blue), SYS_KL (green), DOMAIN_HUB (orange)
  - Link types: tag association (purple), domain membership (orange)
  - Interactive: click nodes for details, fullscreen mode, zoom/pan
  - Legend display with visual explanations
- **API endpoint**: `GET /api/graph` - Returns nodes, links, and statistics

#### RAG Fallback Strategy
- **Problem**: DashScope `sk-sp-` prefix keys don't support embedding API (returns 401)
- **Solution**: Automatic fallback to keyword-only search when vector search fails
- **Implementation**:
  - `RAGSearchService` detects vector search failure
  - Dynamically adjusts weights: keyword weight → 1.0 when no vector results
  - Maintains functionality with reduced precision
- **Validation**: Query "退款规则" successfully returns results via keyword search

#### Enhanced Tag Management
- **Feature**: Add tags to knowledge units for better graph associations
- **Example tags**:
  - 订单退款规则: 退款, 售后, 客户服务, 支付, 7天无理由, 定制商品
  - 用户认证流程: 认证, 登录, 注册, 安全, OAuth, JWT, SSO
  - 支付接口规范: 支付, 接口, API, 支付宝, 微信支付, 银行卡
  - 会员等级体系: 会员, 等级, 积分, VIP, 权益, 优惠
- **Impact**: Graph relationships dynamically update based on shared tags

### 🐛 Bug Fixes

#### Dashboard Statistics
- **Issue**: Dashboard showed 0 knowledge units despite having 4 in database
- **Root cause**: Field name mismatch (frontend expected `bizKlCount`, API returned `biz_kl_count`)
- **Fix**: Updated field mapping in `page.tsx` to match API response format
- **Result**: Dashboard now correctly displays: 业务知识: 2, 系统知识: 2, 健康评分: 81%

#### Knowledge Query End-to-End
- **Issue**: Knowledge query returned no response
- **Root causes**:
  1. API key truncated in `ecosystem.config.cjs` (only 4 chars instead of 38)
  2. Database path relative → absolute path conversion needed
- **Fix**:
  1. Regenerated `ecosystem.config.cjs` with full API keys
  2. Updated `DATABASE_URL` to absolute path: `file:/home/test/pm-knowledge-platform/packages/db/prisma/dev.db`
- **Result**: Full RAG pipeline works: retrieval → LLM generation → citation

#### Embedding Service Degradation
- **Issue**: `EmbeddingService` failed with 401 error (invalid API key for embedding endpoint)
- **Solution**: Implemented graceful degradation
  - `RAGSearchService.fuseResults()` detects empty vector results
  - Adjusts keyword weight to 1.0 when no vector data available
  - Returns keyword-only results with proper scoring
- **Validation**: Query "退款规则" returns "订单退款规则" (score: 0.4) via keyword search

### 🔧 Technical Improvements

#### API Route Registration
- **New route**: `graphRoutes` registered at `/api/graph`
- **File**: `packages/api/src/routes/graph.ts`
- **Functionality**:
  - Fetches all active knowledge units
  - Builds nodes (knowledge units + domain hubs)
  - Calculates links based on shared tags, domains, and content similarity
  - Returns graph data with statistics

#### Sidebar Navigation
- **Update**: Added "知识图谱" link with `Network` icon
- **File**: `packages/web/src/components/layout/Sidebar.tsx`
- **Position**: After "知识浏览", before "知识问答"

#### PM2 Configuration
- **File**: `ecosystem.config.cjs`
- **Changes**:
  - Full API keys (not truncated)
  - Absolute database path
  - Proper environment variable structure

### 📊 Validation Results

**End-to-End Acceptance Test**: 89/100 ✅

| Dimension | Score | Notes |
|-----------|-------|-------|
| Functionality | 95/100 | All core features working, embedding degraded |
| Stability | 90/100 | No crashes, no console errors |
| UX | 85/100 | Clean interface, smooth interactions |
| Performance | 90/100 | Acceptable response times |
| Maintainability | 85/100 | Clear code structure, separated configs |

**Test Coverage**:
- ✅ Login authentication
- ✅ Dashboard statistics
- ✅ Knowledge browsing
- ✅ Knowledge graph visualization (8 nodes, 7 links, 4 domains)
- ✅ Knowledge query (RAG retrieval + LLM generation)
- ✅ Streaming output with citations
- ✅ Tag management
- ✅ Graph dynamic updates
- ✅ Console error checks (all clean)

### 🚀 Deployment

**Server**: 113.98.62.224:55084  
**Tunnel**: https://vegetation-metallica-situated-rep.trycloudflare.com  
**Credentials**: admin@test.com / admin123

**PM2 Processes**:
- `pm-kp-api` (port 3001) - Fastify + Prisma + SQLite
- `pm-kp-web` (port 3000) - Next.js 14

**Database**: SQLite with 4 knowledge units (2 BIZ_KL + 2 SYS_KL)

### 📝 Known Limitations

1. **Vector Embedding**: DashScope `sk-sp-` key doesn't support embedding API
   - **Workaround**: Keyword-only search (functional but less precise)
   - **TODO**: Apply for standard DashScope API key with embedding support

2. **Cloudflare Tunnel URL**: Quick Tunnel URL changes on restart
   - **Workaround**: Manual URL update
   - **TODO**: Configure Named Tunnel with custom domain

3. **Vision API**: Screenshot capture works but vision analysis fails (API key issue)
   - **Impact**: Cannot perform automated visual testing
   - **Workaround**: Manual visual inspection

### 🎓 Lessons Learned

1. **API Key Management**: Always verify full key length in config files
2. **Database Paths**: Use absolute paths in production to avoid working directory issues
3. **Graceful Degradation**: Implement fallback strategies for external service failures
4. **Field Name Consistency**: Ensure frontend/backend field naming conventions match
5. **Graph Visualization**: Start with lightweight libraries (react-force-graph) before considering heavy solutions (Neo4j)

### 🔮 Future Enhancements (P0/P1/P2)

**P0 (High Priority)**:
- [ ] Apply for DashScope standard API key (embedding support)
- [ ] Configure Cloudflare Named Tunnel (stable URL)

**P1 (Medium Priority)**:
- [ ] Integrate GraphRAG for multi-hop reasoning
- [ ] Batch document import with auto-chunking
- [ ] Optimize graph layout for large datasets (>100 nodes)

**P2 (Low Priority)**:
- [ ] User permission management (RBAC)
- [ ] Knowledge version history
- [ ] Additional LLM provider integration

### 📚 References

- **Acceptance Report**: `D:/workspace/ACCEPTANCE-REPORT.md`
- **Project**: pm-knowledge-platform
- **Competitor Analysis**: GraphRAG, Neo4j Bloom, Microsoft GraphRAG, 腾讯云 GraphRAG
- **Visualization Library**: react-force-graph-2d v1.29.1

---

## [6.0.0] - 2026-06-10

### Initial Release

- 9-stage pipeline: brief → align → research → analysis → spec → mvp → ship → operate → grow → retro
- Kanban integration with Hermes profiles
- MVP inner loop (Plan/iter1-3)
- Gate system (G1/G2/G3)
- Human-in-the-loop checkpoints
- Refine deep-dive cycle
- Self-evolution framework

---

**Version Format**: This changelog follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format, and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
