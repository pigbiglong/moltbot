---
name: coding-agent
description: Run Codex CLI, Claude Code, OpenCode, or Pi Coding Agent via background process for programmatic control.
metadata: {"moltbot":{"emoji":"🧩","requires":{"anyBins":["claude","codex","opencode","pi"]}}}
---

# Coding Agent (bash-first)

Use **bash** (with optional background mode) for all coding agent work. Simple and effective.

## ⚠️ PTY Mode Required!

Coding agents (Codex, Claude Code, Pi) are **interactive terminal applications** that need a pseudo-terminal (PTY) to work correctly. Without PTY, you'll get broken output, missing colors, or the agent may hang.

**Always use `pty:true`** when running coding agents:

```bash
# ✅ Correct - with PTY
bash pty:true command:"codex exec 'Your prompt'"

# ❌ Wrong - no PTY, agent may break
bash command:"codex exec 'Your prompt'"
```

### Bash Tool Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `command` | string | The shell command to run |
| `pty` | boolean | **Use for coding agents!** Allocates a pseudo-terminal for interactive CLIs |
| `workdir` | string | Working directory (agent sees only this folder's context) |
| `background` | boolean | Run in background, returns sessionId for monitoring |
| `timeout` | number | Timeout in seconds (kills process on expiry) |
| `elevated` | boolean | Run on host instead of sandbox (if allowed) |

### Process Tool Actions (for background sessions)

| Action | Description |
|--------|-------------|
| `list` | List all running/recent sessions |
| `poll` | Check if session is still running |
| `log` | Get session output (with optional offset/limit) |
| `write` | Send raw data to stdin |
| `submit` | Send data + newline (like typing and pressing Enter) |
| `send-keys` | Send key tokens or hex bytes |
| `paste` | Paste text (with optional bracketed mode) |
| `kill` | Terminate the session |

---

## Quick Start: One-Shot Tasks

For quick prompts/chats, create a temp git repo and run:

```bash
# Quick chat (Codex needs a git repo!)
SCRATCH=$(mktemp -d) && cd $SCRATCH && git init && codex exec "Your prompt here"

# Or in a real project - with PTY!
bash pty:true workdir:~/Projects/myproject command:"codex exec 'Add error handling to the API calls'"
```

**Why git init?** Codex refuses to run outside a trusted git directory. Creating a temp repo solves this for scratch work.

---

## The Pattern: workdir + background + pty

For longer tasks, use background mode with PTY:

```bash
# Start agent in target directory (with PTY!)
bash pty:true workdir:~/project background:true command:"codex exec --full-auto 'Build a snake game'"
# Returns sessionId for tracking

# Monitor progress
process action:log sessionId:XXX

# Check if done
process action:poll sessionId:XXX

# Send input (if agent asks a question)
process action:write sessionId:XXX data:"y"

# Submit with Enter (like typing "yes" and pressing Enter)
process action:submit sessionId:XXX data:"yes"

# Kill if needed
process action:kill sessionId:XXX
```

**Why workdir matters:** Agent wakes up in a focused directory, doesn't wander off reading unrelated files (like your soul.md 😅).

---

## Codex CLI

Codex 是 OpenAI 的本地编码 Agent，提供 CLI 和 IDE 扩展。

```bash
# CLI 使用
bash pty:true workdir:~/project command:"codex exec 'Your task'"

# 单独执行
codex exec "prompt"
```

### 安装方式
```bash
# npm
npm install -g @openai/codex

# Homebrew
brew install --cask codex

# 直接下载二进制
# macOS (Apple Silicon): codex-aarch64-apple-darwin.tar.gz
# Linux: codex-x86_64-unknown-linux-musl.tar.gz
```

### 登录方式
| 方式 | 说明 |
|------|------|
| ChatGPT 账户 | 推荐：Plus/Pro/Team/Edu/Enterprise 计划 |
| API Key | 需要额外配置 |

### IDE 扩展
支持 VS Code、Cursor、Windsurf 编辑器安装

### 主要 Flags
| Flag | Effect |
|------|--------|
| `exec "prompt"` | 一次性执行，完成后退出 |
| `--full-auto` | 沙盒模式，自动批准更改 |
| `--yolo` | 无沙盒，无确认（最快，最危险） | |

### Building/Creating
```bash
# Quick one-shot (auto-approves) - remember PTY!
bash pty:true workdir:~/project command:"codex exec --full-auto 'Build a dark mode toggle'"

# Background for longer work
bash pty:true workdir:~/project background:true command:"codex --yolo 'Refactor the auth module'"
```

### Reviewing PRs

**⚠️ CRITICAL: Never review PRs in Moltbot's own project folder!**
Clone to temp folder or use git worktree.

```bash
# Clone to temp for safe review
REVIEW_DIR=$(mktemp -d)
git clone https://github.com/user/repo.git $REVIEW_DIR
cd $REVIEW_DIR && gh pr checkout 130
bash pty:true workdir:$REVIEW_DIR command:"codex review --base origin/main"
# Clean up after: trash $REVIEW_DIR

# Or use git worktree (keeps main intact)
git worktree add /tmp/pr-130-review pr-130-branch
bash pty:true workdir:/tmp/pr-130-review command:"codex review --base main"
```

### Batch PR Reviews (parallel army!)
```bash
# Fetch all PR refs first
git fetch origin '+refs/pull/*/head:refs/remotes/origin/pr/*'

# Deploy the army - one Codex per PR (all with PTY!)
bash pty:true workdir:~/project background:true command:"codex exec 'Review PR #86. git diff origin/main...origin/pr/86'"
bash pty:true workdir:~/project background:true command:"codex exec 'Review PR #87. git diff origin/main...origin/pr/87'"

# Monitor all
process action:list

# Post results to GitHub
gh pr comment <PR#> --body "<review content>"
```

---

## Claude Code

Claude Code 是 Anthropic 的编码 Agent，支持 CLI、Web、Desktop、IDE 等多种形态。

```bash
# With PTY for proper terminal output
bash pty:true workdir:~/project command:"claude 'Your task'"

# Background
bash pty:true workdir:~/project background:true command:"claude 'Your task'"

# Pipeline mode (streaming output)
tail -f app.log | claude -p "异常时通知我"
```

### 主要功能
- **构建功能**：描述需求 → 制定计划 → 写代码 → 确保运行
- **调试修复**：描述 bug 或粘贴错误信息 → 分析并修复
- **代码库导航**：了解项目结构，查找信息
- **自动化任务**：修复 lint、解决冲突、编写发布说明

### 多平台支持
| 平台 | 说明 |
|------|------|
| CLI | 核心体验，终端运行 `claude` |
| Web | 浏览器访问 claude.ai/code，支持并行任务 |
| Desktop | 独立应用，支持 git worktree 并行会话 |
| VS Code | 原生扩展，内联 diff、@-提及、计划审查 |
| JetBrains | IntelliJ/PyCharm/WebStorm 插件 |
| GitHub Actions | CI 中自动化代码审查、Issue 处理 |
| GitLab CI | MR 和 Issue 驱动自动化 |
| Slack | @mentions 触发任务，返回 PR |
| Chrome | 浏览器连接，实时调试、设计验证 |

### MCP 集成
支持 MCP (Model Context Protocol)，可连接外部数据源：
- Google Drive 读取设计文档
- Figma 获取设计资源
- Slack 协作
- Jira 管理工单

---

## OpenCode

OpenCode 是开源 AI 编码 Agent，提供终端界面、桌面应用、IDE 扩展。

```bash
# 终端使用
bash pty:true workdir:~/project command:"opencode run 'Your task'"

# Docker 运行
docker run -it --rm ghcr.io/anomalyco/opencode
```

### 安装方式
```bash
# 官方脚本
curl -fsSL https://opencode.ai/install | bash

# npm
npm install -g opencode-ai

# Homebrew
brew install anomalyco/tap/opencode

# Windows
choco install opencode
scoop install opencode
```

### 终端要求
需要现代终端模拟器：WezTerm、Alacritty、Ghostty、Kitty

### 配置 Provider
```bash
/connect          # 选择 Provider，前往 opencode.ai/auth 获取 API Key
```

### 初始化项目
```bash
cd /path/to/project
opencode
/init             # 分析项目，创建 AGENTS.md
```

### 使用模式
| 模式 | 切换 | 说明 |
|------|------|------|
| Plan | Tab | 只建议不修改，适合方案讨论 |
| Build | Tab | 执行更改 |

### 核心命令
| 命令 | 说明 |
|------|------|
| `@文件路径` | 直接引用文件，如 `@packages/functions/src/api/index.ts` |
| `/undo` | 撤销上一次更改 |
| `/redo` | 重做更改 |
| `/share` | 生成分享链接 |
| 图片拖拽 | 可将图片拖入终端作为参考 |

### 主要功能
- 解释代码库结构
- 添加新功能（Plan → Build 迭代）
- 直接修改代码
- 支持多 LLM Provider 配置

---

## Pi Coding Agent

```bash
# Install: npm install -g @mariozechner/pi-coding-agent
bash pty:true workdir:~/project command:"pi 'Your task'"

# Non-interactive mode (PTY still recommended)
bash pty:true command:"pi -p 'Summarize src/'"

# Different provider/model
bash pty:true command:"pi --provider openai --model gpt-4o-mini -p 'Your task'"
```

**Note:** Pi now has Anthropic prompt caching enabled (PR #584, merged Jan 2026)!

---

## Parallel Issue Fixing with git worktrees

For fixing multiple issues in parallel, use git worktrees:

```bash
# 1. Create worktrees for each issue
git worktree add -b fix/issue-78 /tmp/issue-78 main
git worktree add -b fix/issue-99 /tmp/issue-99 main

# 2. Launch Codex in each (background + PTY!)
bash pty:true workdir:/tmp/issue-78 background:true command:"pnpm install && codex --yolo 'Fix issue #78: <description>. Commit and push.'"
bash pty:true workdir:/tmp/issue-99 background:true command:"pnpm install && codex --yolo 'Fix issue #99: <description>. Commit and push.'"

# 3. Monitor progress
process action:list
process action:log sessionId:XXX

# 4. Create PRs after fixes
cd /tmp/issue-78 && git push -u origin fix/issue-78
gh pr create --repo user/repo --head fix/issue-78 --title "fix: ..." --body "..."

# 5. Cleanup
git worktree remove /tmp/issue-78
git worktree remove /tmp/issue-99
```

---

## ⚠️ Rules

1. **Always use pty:true** - coding agents need a terminal!
2. **Respect tool choice** - if user asks for Codex, use Codex.
   - Orchestrator mode: do NOT hand-code patches yourself.
   - If an agent fails/hangs, respawn it or ask the user for direction, but don't silently take over.
3. **Be patient** - don't kill sessions because they're "slow"
4. **Monitor with process:log** - check progress without interfering
5. **--full-auto for building** - auto-approves changes
6. **vanilla for reviewing** - no special flags needed
7. **Parallel is OK** - run many Codex processes at once for batch work
8. **NEVER start Codex in ~/clawd/** - it'll read your soul docs and get weird ideas about the org chart!
9. **NEVER checkout branches in ~/Projects/moltbot/** - that's the LIVE Moltbot instance!

---

## Progress Updates (Critical)

When you spawn coding agents in the background, keep the user in the loop.

- Send 1 short message when you start (what's running + where).
- Then only update again when something changes:
  - a milestone completes (build finished, tests passed)
  - the agent asks a question / needs input
  - you hit an error or need user action
  - the agent finishes (include what changed + where)
- If you kill a session, immediately say you killed it and why.

This prevents the user from seeing only "Agent failed before reply" and having no idea what happened.

---

## Auto-Notify on Completion

For long-running background tasks, append a wake trigger to your prompt so Moltbot gets notified immediately when the agent finishes (instead of waiting for the next heartbeat):

```
... your task here.

When completely finished, run this command to notify me:
moltbot gateway wake --text "Done: [brief summary of what was built]" --mode now
```

**Example:**
```bash
bash pty:true workdir:~/project background:true command:"codex --yolo exec 'Build a REST API for todos.

When completely finished, run: moltbot gateway wake --text \"Done: Built todos REST API with CRUD endpoints\" --mode now'"
```

This triggers an immediate wake event — Skippy gets pinged in seconds, not 10 minutes.

---

## Learnings (Jan 2026)

- **PTY is essential:** Coding agents are interactive terminal apps. Without `pty:true`, output breaks or agent hangs.
- **Git repo required:** Codex won't run outside a git directory. Use `mktemp -d && git init` for scratch work.
- **exec is your friend:** `codex exec "prompt"` runs and exits cleanly - perfect for one-shots.
- **submit vs write:** Use `submit` to send input + Enter, `write` for raw data without newline.
- **Sass works:** Codex responds well to playful prompts. Asked it to write a haiku about being second fiddle to a space lobster, got: *"Second chair, I code / Space lobster sets the tempo / Keys glow, I follow"* 🦞
