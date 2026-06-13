# pm-idea-to-mvp v6.1.0

**Production-tested version** with real-world deployment experience.

## 🎯 What's New in v6.1.0

This version is based on v6.0.0 with **proven improvements** from deploying the 产品知识库平台 (pm-knowledge-platform) project:

### ✨ Key Features

1. **Knowledge Graph Visualization** (`/graph`)
   - Interactive force-directed graph using `react-force-graph-2d`
   - Node color coding by type (BIZ_KL/SYS_KL/DOMAIN_HUB)
   - Link visualization for tag/domain associations
   - Fullscreen mode and interactive exploration

2. **RAG Fallback Strategy**
   - Automatic degradation when embedding API fails
   - Keyword-only search maintains functionality
   - Dynamic weight adjustment based on available data

3. **Enhanced Tag Management**
   - Add tags to knowledge units for better graph associations
   - Dynamic relationship calculation based on shared tags
   - Improved knowledge discovery

### 🐛 Critical Fixes

- Dashboard statistics field mapping
- API key truncation in PM2 config
- Database path resolution (relative → absolute)
- Knowledge query end-to-end flow

### 📊 Validation

**Acceptance Score**: 89/100 ✅

- 15/15 core tests passed
- End-to-end RAG pipeline verified
- Knowledge graph visualization working
- No console errors

## 📦 Installation

### Option 1: Use as Reference

Copy the entire `v6.1.0/` directory to your Hermes skills directory:

```bash
cp -r pipelines/pm-idea-to-mvp/v6.1.0 ~/.hermes/skills/pipelines/pm-idea-to-mvp-v6.1.0
```

### Option 2: Merge with v6.0.0

If you want to combine v6.0.0's comprehensive documentation with v6.1.0's practical improvements:

```bash
# Start with v6.0.0 as base
cp -r pipelines/pm-idea-to-mvp pipelines/pm-idea-to-mvp-merged

# Apply v6.1.0 improvements
cp pipelines/pm-idea-to-mvp/v6.1.0/SKILL.md pipelines/pm-idea-to-mvp-merged/SKILL.md
cp pipelines/pm-idea-to-mvp/v6.1.0/CHANGELOG.md pipelines/pm-idea-to-mvp-merged/CHANGELOG.md
```

## 🔍 Differences from v6.0.0

| Aspect | v6.0.0 | v6.1.0 |
|--------|--------|--------|
| **Lines** | 780 | 361 |
| **Focus** | Comprehensive documentation | Production-tested features |
| **Knowledge Graph** | Not included | ✅ Full implementation |
| **RAG Fallback** | Not included | ✅ Keyword degradation |
| **Tag Management** | Not included | ✅ Enhanced associations |
| **Real-world Validation** | Theoretical | ✅ 89/100 acceptance score |
| **Deployment Guide** | Generic | ✅ Specific server config |

## 🚀 Quick Start

### Using v6.1.0 for New Projects

1. Load the skill:
   ```
   skill_view(name='pm-idea-to-mvp-v6.1.0')
   ```

2. Follow the pipeline stages (same as v6.0.0):
   - Stage 0-4: Brief → Align → Research → Analysis → Spec
   - Stage 5: MVP (with knowledge graph if applicable)
   - Stage 6-9: Ship → Operate → Grow → Retro

3. For knowledge-intensive projects, consider adding:
   - Knowledge graph visualization page
   - RAG fallback strategy
   - Tag management system

### Migrating from v6.0.0

If you're already using v6.0.0 and want to add v6.1.0 features:

1. **Knowledge Graph**:
   - Copy `packages/api/src/routes/graph.ts` to your project
   - Register route in `packages/api/src/index.ts`
   - Install `react-force-graph-2d`: `pnpm add react-force-graph-2d`
   - Create `packages/web/src/app/graph/page.tsx`
   - Add navigation link in Sidebar

2. **RAG Fallback**:
   - Update `RAGSearchService.fuseResults()` to detect empty vector results
   - Adjust keyword weight dynamically

3. **Tag Management**:
   - Add tag update API endpoint
   - Create UI for tag management
   - Update graph calculation to include tag associations

## 📖 Documentation

- **CHANGELOG.md**: Detailed list of changes and improvements
- **SKILL.md**: Full pipeline documentation (361 lines)
- **ACCEPTANCE-REPORT.md**: End-to-end validation results (available in project root)

## 🎓 Lessons Learned

1. **API Key Management**: Always verify full key length in config files
2. **Database Paths**: Use absolute paths in production
3. **Graceful Degradation**: Implement fallback strategies for external service failures
4. **Field Name Consistency**: Ensure frontend/backend naming conventions match
5. **Graph Visualization**: Start lightweight, scale as needed

## 🔮 Future Roadmap

### P0 (High Priority)
- [ ] Vector embedding support (requires standard DashScope API key)
- [ ] Stable Cloudflare Named Tunnel

### P1 (Medium Priority)
- [ ] GraphRAG integration for multi-hop reasoning
- [ ] Batch document import
- [ ] Large-scale graph optimization

### P2 (Low Priority)
- [ ] User permission management (RBAC)
- [ ] Knowledge version history
- [ ] Additional LLM providers

## 📝 Notes

- This version is **production-tested** on 产品知识库平台 project
- All features have been validated with real users
- Documentation is concise (361 lines vs 780 lines in v6.0.0)
- Focus on **practical implementation** over theoretical framework

## 🤝 Contributing

If you find issues or have improvements:

1. Create a new version directory (e.g., `v6.2.0/`)
2. Copy from `v6.1.0/` as base
3. Make your changes
4. Update CHANGELOG.md
5. Submit PR for review

**Do NOT modify v6.0.0 or v6.1.0 directly** - create new versions instead.

## 📄 License

MIT License - same as v6.0.0

## 🔗 Related

- **v6.0.0**: Original comprehensive pipeline (780 lines)
- **Project**: pm-knowledge-platform (production deployment)
- **Server**: 113.98.62.224:55084
- **Tunnel**: https://vegetation-metallica-situated-rep.trycloudflare.com

---

**Version**: 6.1.0  
**Release Date**: 2026-06-13  
**Status**: ✅ Production-ready
