<div align="center">

# 📤 ipub

**把你的技术笔记变成可发布的内容。**

*在笔记里写，一键发布到所有平台。*

[English](README.md) | [简体中文](README.zh-CN.md)

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Claude](https://img.shields.io/badge/Powered%20by-Claude-blueviolet?style=for-the-badge&logo=anthropic&logoColor=white)](https://anthropic.com)

---

🔍 **扫描**笔记 → 📝 **生成**发布草稿 → 👀 **审核**并编辑 → 📤 **导出**到各平台

</div>

---

## 🤔 你是不是也有这些烦恼？

你写了大量技术笔记——实验记录、论文阅读、部署指南、踩坑日志。**但它们从来没有被发布过。** 为什么？

- 📂 笔记散落在 Obsidian、飞书、本地 Markdown、GitHub 各处
- 🎨 每个平台需要不同的格式（CSDN、知乎、飞书、博客……）
- ⏰ 把原始笔记打磨成一篇像样的文章太花时间
- 🤖 你不想让 AI *替*你写——你想让它*帮*你润色

**ipub 就是连接「原始笔记」和「发布内容」之间的桥梁。**

---

## ✨ ipub 做什么

```
你的笔记 (Markdown、Obsidian、实验日志……)
         │
         ▼
    ┌──────────┐
    │   scan   │  ← 发现值得发布的笔记
    └────┬─────┘
         ▼
    ┌──────────┐
    │  draft   │  ← LLM 润色为可发布格式
    └────┬─────┘
         ▼
    ┌──────────┐
    │  review  │  ← 你来审核、编辑、确认
    └────┬─────┘
         ▼
    ┌──────────┐
    │ approve  │  ← 导出到各平台格式
    └──────────┘
         │
         ▼
  博客 · CSDN · 知乎 · 飞书
```

### 核心原则

| 原则 | 含义 |
|------|------|
| 🙋 **你是作者** | ipub 润色你的文字，绝不替代你 |
| ✅ **人工审批** | 没有你的明确同意，什么都不会发布 |
| 🎯 **平台感知** | 一篇笔记 → 多个平台优化版本 |
| 📁 **本地优先** | 所有数据都在你的机器上，不依赖云端 |
| 🔌 **零锁定** | 一切都是 Markdown + YAML，随时可以带走 |

---

## 🚀 快速开始

### 安装

```bash
# 从源码安装
git clone https://github.com/wbzuo/ipub.git
cd ipub
pip install -e ".[llm]"

# 设置 API Key
export ANTHROPIC_API_KEY="your-key-here"
```

### 30 秒上手

```bash
# 1. 在笔记目录初始化 ipub
cd ~/my-notes
ipub init

# 2. 扫描目录，找出值得发布的笔记
ipub scan ./

# 3. 为某篇笔记生成草稿
ipub draft ./tent-reproduce.md -p blog -p csdn

# 4. 审核草稿
ipub review 001

# 5. 确认并导出
ipub approve 001
```

完成！润色好的、适配各平台格式的 Markdown 文件已经在 `.ipub/export/` 目录里了。

---

## 📖 命令详解

### `ipub init` — 初始化

在当前目录初始化 ipub，创建 `ipub.yaml` 配置文件和 `.ipub/` 数据目录。

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

### `ipub scan <目录>` — 扫描笔记

扫描指定目录中的笔记，识别哪些值得发布。每篇笔记会得到一个 **可发布评分**（0.0 ~ 1.0）。

```bash
ipub scan ./notes
ipub scan ./notes --min-score 0.7    # 只显示高质量候选
```

```
Found 12 note file(s). Evaluating...

                   可发布候选
┌───────┬──────────────────────────────┬──────────┬───────┬────────┐
│ 评分  │ 标题                         │ 类型     │ 字数  │ 风险   │
├───────┼──────────────────────────────┼──────────┼───────┼────────┤
│  0.9  │ Tent 复现完整记录            │ 教程     │  2340 │ -      │
│  0.8  │ Docker 多阶段构建踩坑        │ 实战     │  1820 │ -      │
│  0.7  │ ViT 论文精读笔记            │ 分析     │  3100 │ -      │
│  0.5  │ 会议记录 0412               │ 笔记     │   450 │ 草稿   │
└───────┴──────────────────────────────┴──────────┴───────┴────────┘

Found 4 candidate(s).
```

**评分指南：**

| 评分 | 含义 |
|------|------|
| 🟢 **0.8 - 1.0** | 可直接发布，结构完整 |
| 🟡 **0.6 - 0.8** | 内容不错，需要少量编辑 |
| 🟠 **0.4 - 0.6** | 有价值但需要大幅修改 |
| 🔴 **< 0.4** | 不适合发布（碎片、太短、私密内容） |

---

### `ipub draft <文件>` — 生成草稿

从一篇笔记生成可发布的草稿。LLM 会润色你的文字，同时保留你的个人风格。

```bash
ipub draft ./notes/tent-reproduce.md                    # 默认：博客格式
ipub draft ./notes/tent-reproduce.md -p blog -p csdn    # 多平台
ipub draft ./notes/tent-reproduce.md -p zhihu -p feishu # 更多平台
```

```
Generating draft from: tent-reproduce.md
  Title: 从零复现 Tent：环境配置、代码解读与实验分析
  Summary: 完整记录 Tent 论文的复现过程，包括环境搭建、核心代码解读...
  Alt titles: Tent 复现避坑指南, 手把手复现 Tent...
Draft created: 001
  Review: ipub review 001
```

**草稿目录结构：**

```
.ipub/drafts/001-从零复现-tent/
├── original.md           # 你的原始笔记（不会被修改）
├── draft.md              # 润色后的完整文章
├── meta.yaml             # 标题、摘要、状态、风险标记
└── platform/
    ├── blog.md           # 博客优化版
    ├── csdn.md           # CSDN 优化版
    ├── zhihu.md          # 知乎优化版
    └── feishu.md         # 飞书优化版
```

---

### `ipub review [draft_id]` — 审核草稿

查看所有待审核草稿，或查看某篇草稿的详细信息。

```bash
ipub review          # 查看所有草稿
ipub review 001      # 查看 001 号草稿详情
```

**列表视图：**

```
                           草稿列表
┌────┬────────────────────────────────┬─────────┬───────────┬────────────┐
│ ID │ 标题                           │ 状态    │ 平台      │ 创建日期    │
├────┼────────────────────────────────┼─────────┼───────────┼────────────┤
│ 001│ 从零复现 Tent                  │ 待审核  │ blog,csdn │ 2026-04-15 │
│ 002│ Docker 多阶段构建踩坑          │ 待审核  │ blog      │ 2026-04-15 │
│ 003│ ViT 论文精读                   │ 已通过  │ zhihu     │ 2026-04-14 │
└────┴────────────────────────────────┴─────────┴───────────┴────────────┘
```

**详情视图**（`ipub review 001`）：

```
╭──────────────────── 草稿 001 ────────────────────╮
│ 标题：从零复现 Tent：环境配置、代码解读与实验分析    │
│ 摘要：完整记录 Tent 论文的复现过程...                │
│ 状态：pending_review                                │
│ 平台：blog, csdn                                    │
│ 来源：/home/user/notes/tent-reproduce.md             │
│ 风险：无                                            │
╰─────────────────────────────────────────────────────╯

备选标题：
  1. Tent 复现避坑指南：从环境搭建到实验结果
  2. 手把手复现 Tent：完整流程与踩坑记录
  3. Tent 论文复现实录

╭──────────────── 草稿预览 ─────────────────╮
│ # 从零复现 Tent                           │
│                                           │
│ > Tent 是一篇经典的 Test-Time Adaptation  │
│ > 论文...                                 │
│ ...                                       │
╰───────────────────────────────────────────╯

通过：ipub approve 001
驳回：ipub reject 001
```

---

### `ipub approve <draft_id>` — 通过并导出

通过审核并导出适配各平台的 Markdown 文件。

```bash
ipub approve 001                          # 导出所有平台版本
ipub approve 001 -p blog                  # 只导出博客版本
ipub approve 001 -o ~/blog/content/posts  # 导出到指定目录
```

```
  Exported [blog]: .ipub/export/001-从零复现-tent-blog.md
  Exported [csdn]: .ipub/export/001-从零复现-tent-csdn.md

Draft 001 approved and exported.
```

---

### `ipub reject <draft_id>` — 驳回草稿

驳回不满意的草稿。

```bash
ipub reject 002
ipub reject 002 -r "语气太正式了，需要重写"
```

---

## ⚙️ 配置说明

`ipub init` 会生成一个 `ipub.yaml` 配置文件，默认配置如下：

```yaml
# ipub.yaml

# 项目名称
project: my-notes

# LLM 设置
llm:
  provider: anthropic          # 或 "stdin" 手动模式
  model: claude-sonnet-4-20250514

# 扫描设置
scan:
  extensions: [.md, .txt]      # 扫描的文件类型
  ignore:                      # 忽略的目录
    - node_modules
    - .git
    - .ipub
    - __pycache__
  min_words: 100               # 跳过少于此字数的笔记

# 平台设置
platforms:
  blog:
    format: markdown
    max_length: null            # 无字数限制
  csdn:
    format: markdown
    max_length: null
  zhihu:
    format: markdown
    max_length: null
  feishu:
    format: markdown
    max_length: null

# 写作风格
style:
  tone: technical              # 写作风格
  avoid_phrases:               # LLM 应避免使用的短语
    - 众所周知
    - 值得一提的是
    - 本文将
  language: zh                 # 输出语言
```

### 没有 API Key？没关系。

将 `provider` 设为 `stdin`，ipub 会把 prompt 打印出来，你可以手动粘贴到任何 LLM 中使用：

```yaml
llm:
  provider: stdin
```

---

## 🗂️ 目录结构

运行 `ipub init` 后的目录结构：

```
my-notes/
├── ipub.yaml                    # 配置文件
├── .ipub/                       # ipub 数据目录（建议加入 .gitignore）
│   ├── candidates.yaml          # 扫描结果
│   ├── published.yaml           # 发布历史
│   ├── drafts/                  # 所有草稿
│   │   ├── 001-从零复现-tent/
│   │   │   ├── original.md      # 原始笔记
│   │   │   ├── draft.md         # 润色版本
│   │   │   ├── meta.yaml        # 元数据和状态
│   │   │   └── platform/        # 各平台版本
│   │   │       ├── blog.md
│   │   │       ├── csdn.md
│   │   │       └── zhihu.md
│   │   └── 002-docker-踩坑/
│   │       └── ...
│   └── export/                  # 审核通过后的导出文件
│       ├── 001-从零复现-tent-blog.md
│       └── 001-从零复现-tent-csdn.md
├── notes/                       # 你的笔记目录（不会被修改）
│   ├── tent-reproduce.md
│   ├── docker-multistage.md
│   └── ...
```

---

## 🔄 典型工作流

### 日常工作流

```bash
# 早上：扫描新笔记
ipub scan ./notes

# 发现好内容？生成草稿
ipub draft ./notes/new-finding.md -p blog -p csdn

# 审核并通过
ipub review 004
ipub approve 004

# 复制到博客目录，粘贴到 CSDN
# 搞定！
```

### 批量工作流

```bash
# 扫描所有笔记
ipub scan ./notes --min-score 0.7

# 批量生成草稿
ipub draft ./notes/paper-a.md -p blog
ipub draft ./notes/paper-b.md -p blog -p zhihu
ipub draft ./notes/debug-log.md -p csdn

# 统一审核
ipub review

# 通过好的，驳回差的
ipub approve 001
ipub approve 003
ipub reject 002 -r "结果部分需要更多细节"
```

---

## 🎯 平台支持

| 平台 | 状态 | 输出格式 |
|------|------|---------|
| 📝 博客 (Hugo/VitePress/Jekyll) | ✅ 已支持 | 带 frontmatter 的 Markdown |
| 📘 CSDN | ✅ 已支持 | CSDN 格式 Markdown |
| 💡 知乎 | ✅ 已支持 | 知乎风格 Markdown |
| 📄 飞书 | ✅ 已支持 | 飞书兼容 Markdown |
| 🐦 X / Twitter | 🔜 计划中 | 推文串格式 |
| 📕 小红书 | 🔜 计划中 | 短内容格式 |
| 🔔 微信公众号 | 🔜 计划中 | 公众号文章格式 |

> **说明：** v0.1 版本生成各平台优化的 Markdown 文件，需要手动复制粘贴到平台发布。
> v0.2+ 版本计划支持通过 API 自动发布。

---

## 🧠 LLM 的工作方式

ipub 使用 Claude 做三件事——**仅仅三件事**：

### 1. 评估（`scan` 时）
> "这篇笔记是否足够完整，可以发布？它属于什么类型的内容？"

### 2. 润色（`draft` 时）
> "改善结构，修正格式，但保留作者的风格和语气。"

### 3. 适配（`draft` 时）
> "将内容适配为 CSDN / 知乎 / 飞书 的排版风格。"

**ipub 绝不会做的事：**
- ❌ 凭空生成内容
- ❌ 添加你没有写过的观点或结论
- ❌ 未经你确认就发布
- ❌ 将你的数据发送到 LLM API 之外的任何地方

---

## 🛡️ 隐私与安全

- 🔒 **本地优先** — 所有数据都保存在你机器上的 `.ipub/` 目录中
- 🔑 **你自己的 API Key** — LLM 调用使用你自己的 Anthropic API Key
- 👀 **风险检测** — ipub 会在发布前标记敏感内容（本地路径、内部信息等）
- 📋 **完整可追溯** — 每篇草稿都关联回源笔记

---

## 🗺️ 路线图

- [x] **v0.1** — 核心 CLI：扫描、生成草稿、审核、通过、导出
- [ ] **v0.2** — 通过 API 自动发布到飞书
- [ ] **v0.3** — 风格学习（记住你的编辑偏好）
- [ ] **v0.4** — 更多平台支持（公众号、X、小红书）
- [ ] **v0.5** — 监听模式（自动发现新笔记）
- [ ] **v0.6** — Claude Code 技能集成（`/ipub scan`）
- [ ] **v0.7** — Web 审核面板

---

## 🤝 贡献指南

欢迎贡献！以下是需要帮助的方向：

- 🔌 **平台连接器** — 为新平台添加自动发布支持
- 🌍 **国际化** — 英文 prompt 模板和文档
- 🧪 **测试** — scanner、drafter、reviewer 的单元测试
- 📝 **模板** — 各平台特定的排版模板

---

## 📄 许可证

MIT

---

<div align="center">

**ipub** — 在笔记里写，一键发布到所有平台。

[报告 Bug](https://github.com/wbzuo/ipub/issues) · [功能建议](https://github.com/wbzuo/ipub/issues)

</div>
