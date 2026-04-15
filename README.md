<div align="center">

# 📤 ipub

**Turn your technical notes into publishable content.**

*Write in your notes. Publish everywhere.*

[English](README.md) | [简体中文](README.zh-CN.md)

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Claude](https://img.shields.io/badge/Powered%20by-Claude-blueviolet?style=for-the-badge&logo=anthropic&logoColor=white)](https://anthropic.com)

---

🔍 **Scan** your notes → 📝 **Draft** publishable content → 👀 **Review** & edit → 📤 **Export** to any platform

</div>

---

## 🤔 The Problem

You write tons of technical notes — experiment logs, paper reviews, deployment guides, bug fixes. **But they never get published.** Why?

- 📂 Notes are scattered across Obsidian, Feishu, local markdown, GitHub
- 🎨 Every platform needs different formatting (CSDN, Zhihu, Feishu, blog...)
- ⏰ Editing raw notes into polished articles takes too long
- 🤖 You don't want AI to write *for* you — you want it to polish *your* work

**ipub bridges the gap between your raw notes and published content.**

---

## ✨ What ipub Does

```
Your Notes (markdown, Obsidian, experiment logs...)
         │
         ▼
    ┌─────────┐
    │  scan   │  ← Find notes worth publishing
    └────┬────┘
         ▼
    ┌─────────┐
    │  draft  │  ← LLM polishes into publishable format
    └────┬────┘
         ▼
    ┌─────────┐
    │ review  │  ← You review, edit, approve
    └────┬────┘
         ▼
    ┌─────────┐
    │ approve │  ← Export for each platform
    └─────────┘
         │
         ▼
  Blog · CSDN · Zhihu · Feishu
```

### Key Principles

| Principle | What it means |
|-----------|---------------|
| 🙋 **You are the author** | ipub polishes your writing, never replaces it |
| ✅ **Human-in-the-loop** | Nothing gets published without your explicit approval |
| 🎯 **Platform-aware** | One note → multiple platform-optimized versions |
| 📁 **Local-first** | All data stays on your machine, no cloud dependency |
| 🔌 **Zero lock-in** | Everything is markdown + YAML, take it anywhere |

---

## 🚀 Quick Start

### Installation

```bash
# Install from source
git clone https://github.com/wbzuo/ipub.git
cd ipub
pip install -e ".[llm]"

# Set your API key
export ANTHROPIC_API_KEY="your-key-here"
```

### 30-Second Demo

```bash
# 1. Initialize ipub in your notes directory
cd ~/my-notes
ipub init

# 2. Scan for publishable notes
ipub scan ./

# 3. Draft a specific note
ipub draft ./tent-reproduce.md -p blog -p csdn

# 4. Review the draft
ipub review 001

# 5. Approve and export
ipub approve 001
```

That's it. Your polished, platform-ready markdown is in `.ipub/export/`.

---

## 📖 Commands

### `ipub init`

Initialize ipub in the current directory. Creates `ipub.yaml` config and `.ipub/` data directory.

```bash
ipub init
```

```
Initialized ipub.
  Config: /home/user/notes/ipub.yaml
  Data:   .ipub/

Next: ipub scan <notes-directory>
```

---

### `ipub scan <directory>`

Scan a directory of notes and identify which ones are worth publishing. Each note gets a **publishability score** from 0.0 to 1.0.

```bash
ipub scan ./notes
ipub scan ./notes --min-score 0.7    # Only show high-quality candidates
```

```
Found 12 note file(s). Evaluating...

              Publishable Candidates
┌───────┬──────────────────────────────┬──────────┬───────┬────────┐
│ Score │ Title                        │ Type     │ Words │ Risks  │
├───────┼──────────────────────────────┼──────────┼───────┼────────┤
│  0.9  │ Tent 复现完整记录            │ tutorial │  2340 │ -      │
│  0.8  │ Docker 多阶段构建踩坑        │ writeup  │  1820 │ -      │
│  0.7  │ ViT 论文精读笔记            │ analysis │  3100 │ -      │
│  0.5  │ 会议记录 0412               │ notes    │   450 │ draft  │
└───────┴──────────────────────────────┴──────────┴───────┴────────┘

Found 4 candidate(s).
```

**Scoring guide:**

| Score | Meaning |
|-------|---------|
| 🟢 **0.8 - 1.0** | Directly publishable, well-structured |
| 🟡 **0.6 - 0.8** | Good content, needs some editing |
| 🟠 **0.4 - 0.6** | Has value but needs significant work |
| 🔴 **< 0.4** | Not suitable (fragment, too short, private) |

---

### `ipub draft <file>`

Generate a publishable draft from a note. The LLM polishes your writing while preserving your voice.

```bash
ipub draft ./notes/tent-reproduce.md                    # Default: blog format
ipub draft ./notes/tent-reproduce.md -p blog -p csdn    # Multiple platforms
ipub draft ./notes/tent-reproduce.md -p zhihu -p feishu # More platforms
```

```
Generating draft from: tent-reproduce.md
  Title: 从零复现 Tent：环境配置、代码解读与实验分析
  Summary: 完整记录 Tent 论文的复现过程，包括环境搭建、核心代码解读...
  Alt titles: Tent 复现避坑指南, 手把手复现 Tent...
Draft created: 001
  Review: ipub review 001
```

**What the draft includes:**

```
.ipub/drafts/001-从零复现-tent/
├── original.md           # Your original note (untouched)
├── draft.md              # Polished full article
├── meta.yaml             # Title, summary, status, risks
└── platform/
    ├── blog.md           # Blog-optimized version
    ├── csdn.md           # CSDN-optimized version
    ├── zhihu.md          # Zhihu-optimized version
    └── feishu.md         # Feishu-optimized version
```

---

### `ipub review [draft_id]`

Review all pending drafts, or inspect a specific one.

```bash
ipub review          # List all drafts
ipub review 001      # Show draft 001 in detail
```

**List view:**

```
                         Drafts
┌────┬────────────────────────────────┬─────────┬───────────┬────────────┐
│ ID │ Title                          │ Status  │ Platforms │ Created    │
├────┼────────────────────────────────┼─────────┼───────────┼────────────┤
│ 001│ 从零复现 Tent                  │ pending │ blog,csdn │ 2026-04-15 │
│ 002│ Docker 多阶段构建踩坑          │ pending │ blog      │ 2026-04-15 │
│ 003│ ViT 论文精读                   │ approved│ zhihu     │ 2026-04-14 │
└────┴────────────────────────────────┴─────────┴───────────┴────────────┘
```

**Detail view** (`ipub review 001`):

```
╭──────────────────── Draft 001 ────────────────────╮
│ Title: 从零复现 Tent：环境配置、代码解读与实验分析  │
│ Summary: 完整记录 Tent 论文的复现过程...            │
│ Status: pending_review                             │
│ Platforms: blog, csdn                              │
│ Source: /home/user/notes/tent-reproduce.md          │
│ Risks: none                                        │
╰────────────────────────────────────────────────────╯

Alternative titles:
  1. Tent 复现避坑指南：从环境搭建到实验结果
  2. 手把手复现 Tent：完整流程与踩坑记录
  3. Tent 论文复现实录

╭──────────────── Draft Preview ─────────────────╮
│ # 从零复现 Tent                                │
│                                                │
│ > Tent 是一篇经典的 Test-Time Adaptation 论文..│
│ ...                                            │
╰────────────────────────────────────────────────╯

Approve: ipub approve 001
Reject:  ipub reject 001
```

---

### `ipub approve <draft_id>`

Approve a draft and export platform-ready markdown files.

```bash
ipub approve 001                          # Export all platforms
ipub approve 001 -p blog                  # Export only blog version
ipub approve 001 -o ~/blog/content/posts  # Export to custom directory
```

```
  Exported [blog]: .ipub/export/001-从零复现-tent-blog.md
  Exported [csdn]: .ipub/export/001-从零复现-tent-csdn.md

Draft 001 approved and exported.
```

---

### `ipub reject <draft_id>`

Reject a draft that doesn't meet your standards.

```bash
ipub reject 002
ipub reject 002 -r "tone is too formal, needs rewrite"
```

---

## ⚙️ Configuration

`ipub init` generates an `ipub.yaml` with sensible defaults:

```yaml
# ipub.yaml
project: my-notes

# LLM settings
llm:
  provider: anthropic          # or "stdin" for manual mode
  model: claude-sonnet-4-20250514

# Scanning settings
scan:
  extensions: [.md, .txt]      # File types to scan
  ignore:                      # Directories to skip
    - node_modules
    - .git
    - .ipub
    - __pycache__
  min_words: 100               # Skip notes shorter than this

# Platform settings
platforms:
  blog:
    format: markdown
    max_length: null
  csdn:
    format: markdown
    max_length: null
  zhihu:
    format: markdown
    max_length: null
  feishu:
    format: markdown
    max_length: null

# Writing style
style:
  tone: technical              # Your writing tone
  avoid_phrases:               # Phrases the LLM should NOT use
    - 众所周知
    - 值得一提的是
    - 本文将
  language: zh                 # Output language
```

### No API Key? No Problem.

Set `provider: stdin` and ipub will print the prompt for you to paste into any LLM manually:

```yaml
llm:
  provider: stdin
```

---

## 🗂️ Project Structure

After running `ipub init`, your directory looks like:

```
my-notes/
├── ipub.yaml                    # Configuration
├── .ipub/                       # ipub data (gitignore this)
│   ├── candidates.yaml          # Scan results
│   ├── published.yaml           # Publish history
│   ├── drafts/                  # All drafts
│   │   ├── 001-从零复现-tent/
│   │   │   ├── original.md      # Your original note
│   │   │   ├── draft.md         # Polished version
│   │   │   ├── meta.yaml        # Metadata & status
│   │   │   └── platform/        # Platform variants
│   │   │       ├── blog.md
│   │   │       ├── csdn.md
│   │   │       └── zhihu.md
│   │   └── 002-docker-踩坑/
│   │       └── ...
│   └── export/                  # Approved & exported files
│       ├── 001-从零复现-tent-blog.md
│       └── 001-从零复现-tent-csdn.md
├── notes/                       # Your actual notes (unchanged)
│   ├── tent-reproduce.md
│   ├── docker-multistage.md
│   └── ...
```

---

## 🔄 Typical Workflow

### Daily workflow

```bash
# Morning: scan for new publishable notes
ipub scan ./notes

# Found something good? Draft it
ipub draft ./notes/new-finding.md -p blog -p csdn

# Review and approve
ipub review 004
ipub approve 004

# Copy to your blog, paste to CSDN
# Done!
```

### Batch workflow

```bash
# Scan everything
ipub scan ./notes --min-score 0.7

# Draft the top candidates
ipub draft ./notes/paper-a.md -p blog
ipub draft ./notes/paper-b.md -p blog -p zhihu
ipub draft ./notes/debug-log.md -p csdn

# Review all at once
ipub review

# Approve the good ones
ipub approve 001
ipub approve 003
ipub reject 002 -r "needs more detail on results"
```

---

## 🎯 Supported Platforms

| Platform | Status | Output |
|----------|--------|--------|
| 📝 Blog (Hugo/VitePress/Jekyll) | ✅ Ready | Markdown with frontmatter |
| 📘 CSDN | ✅ Ready | CSDN-formatted markdown |
| 💡 Zhihu | ✅ Ready | Zhihu-style markdown |
| 📄 Feishu | ✅ Ready | Feishu-compatible markdown |
| 🐦 X / Twitter | 🔜 Planned | Thread format |
| 📕 小红书 | 🔜 Planned | Short-form content |
| 🔔 公众号 | 🔜 Planned | WeChat article format |

> **Note:** v0.1 generates platform-optimized markdown files. You copy-paste to publish.
> Auto-publishing via API is planned for v0.2+.

---

## 🧠 How the LLM Works

ipub uses Claude to do three things — and **only** three things:

### 1. Evaluate (during `scan`)
> "Is this note complete enough to publish? What type of content is it?"

### 2. Polish (during `draft`)
> "Improve the structure, fix formatting, but keep the author's voice."

### 3. Adapt (during `draft`)
> "Reformat this for CSDN / Zhihu / Feishu style."

**What ipub does NOT do:**
- ❌ Generate content from scratch
- ❌ Add claims or conclusions you didn't write
- ❌ Publish without your approval
- ❌ Send your data anywhere except the LLM API

---

## 🛡️ Privacy & Security

- 🔒 **Local-first** — all data stays in `.ipub/` on your machine
- 🔑 **Your API key** — LLM calls use your own Anthropic API key
- 👀 **Risk detection** — ipub flags sensitive content (local paths, internal info) before publishing
- 📋 **Full traceability** — every draft links back to its source note

---

## 🗺️ Roadmap

- [x] **v0.1** — Core CLI: scan, draft, review, approve, export
- [ ] **v0.2** — Auto-publish to Feishu via API
- [ ] **v0.3** — Style learning (remember your editing preferences)
- [ ] **v0.4** — More platforms (公众号, X, 小红书)
- [ ] **v0.5** — Watch mode (auto-detect new notes)
- [ ] **v0.6** — Claude Code skill (`/ipub scan`)
- [ ] **v0.7** — Web dashboard for review

---

## 🤝 Contributing

Contributions welcome! Areas that need help:

- 🔌 **Platform connectors** — add auto-publish support for new platforms
- 🌍 **i18n** — English prompt templates and documentation
- 🧪 **Testing** — unit tests for scanner, drafter, reviewer
- 📝 **Templates** — platform-specific formatting templates

---

## 📄 License

MIT

---

<div align="center">

**ipub** — Write in your notes. Publish everywhere.

[Report Bug](https://github.com/wbzuo/ipub/issues) · [Request Feature](https://github.com/wbzuo/ipub/issues)

</div>
