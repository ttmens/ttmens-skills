---
name: prd-template
description: >-
  Generate structured PRD documents with goals, users, features, and acceptance
  criteria. Use during idea-to-product design phase or when user asks for PRD.
version: 1.0.0
author: ttmens
license: MIT
---

# PRD Template

生成结构化产品需求文档，保存到 `docs/prd/YYYY-MM-DD-<feature>.md`。

## Template

```markdown
# PRD: [功能名]

## 背景与问题
## 目标用户
## 目标与非目标
## 用户故事
| ID | 作为 | 我希望 | 以便 |
## 功能需求
| ID | 需求 | 优先级 | 验收标准 |
## 非功能需求
## 验收标准（分域）
- functional: ...
- ux: ...
- ops: ...
## 开放问题
```

## Workflow

1. 从 discovery.md / research.md 提取输入
2. 填写模板，中文输出
3. 链接到 workflow_state artifacts
