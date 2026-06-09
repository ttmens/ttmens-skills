---
name: user-journey
description: "PM-style user journey maps driving page design and information architecture."
version: 1.0.0
author: PM Pipeline
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [product-management, ux, journey, prd]
    related_skills: [open-design, ui-ux-pro-max, pm-idea-to-mvp]
---

# User Journey — Journey-Driven Product Design

Think like a **product manager**: map personas through scenarios, then derive screens and information priority.

## Output

Write `03b-user-journey.md` in the project directory:

```markdown
# 用户旅程地图

## Personas
| ID | 角色 | 目标 | 痛点 |
|----|------|------|------|
| P1 | ... | ... | ... |

## 核心旅程
| 旅程ID | Persona | 阶段 | 用户行为 | 系统响应 | Touchpoint | 情绪/痛点 |
|--------|---------|------|----------|----------|------------|-----------|

## 屏幕映射
| 屏幕 | 旅程ID | 信息优先级（首屏必见） | 关联 US |
|------|--------|------------------------|---------|

## 核心路径（≤3）
1. ...
```

## Process

1. Read `03-prd.md`, `CONTEXT.md`, `02-analysis.md`
2. Define ≥3 personas and ≥5 touchpoints across journeys
3. Map each user story (US-*) to journey touchpoint IDs
4. Derive screen list and per-screen information hierarchy
5. **pm-planner**: update `03-prd.md` so stories trace to journey IDs
6. **open-design**: prototype screens must cover core paths from this doc
7. **pm-builder**: MVP README 核心流程编号须与本文一致

## Rules

- 所有面向用户文案使用**简体中文**
- 每条旅程须有明确成功标准
- Agent/系统类 persona 若为核心用户，必须单独列出（如 IDE/Agent 消费知识包）

## Verification

- ≥3 personas, ≥5 touchpoints
- 屏幕映射表非空
- `03-prd.md` 含 touchpoint 或旅程 ID 引用
