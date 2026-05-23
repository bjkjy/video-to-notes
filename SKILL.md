---
name: video-to-notes
description: >
  将视频/音频自动转换为结构化学习笔记。支持 B站、YouTube、抖音、小红书、播客等平台。
  使用 yt-dlp 下载媒体，Whisper 语音转文字，然后生成带思维导图、时间复杂度对比、选择指南的专业学习笔记。
  触发关键词："把这个视频转成笔记"、"视频转学习笔记"、"帮我分析这个视频"、"生成学习笔记"、"整理视频内容"、
  "convert video to notes"、"summarize this video"、"video to markdown"。
  当用户提供视频 URL 或想要从视频中提取知识时使用此技能。
author: bjk
homepage: https://github.com/bjkjy/video-to-notes
version: "1.0.0"
tags: ['video', 'notes', 'whisper', 'yt-dlp', 'learning', 'education', 'bilibili', 'youtube']
metadata:
  openclaw:
    emoji: "🎬"
    requires:
      bins: [yt-dlp, python3]
      pip: [openai-whisper]
---

# Video to Notes - 视频转学习笔记

将任意视频或音频自动转换为结构化、可复习的学习笔记。

## 工作流总览

```
输入: 视频 URL 或 本地文件
    │
    ▼
┌──────────────────────┐
│  Step 0: 前置澄清    │  Inversion 模式：先问后做
│  补齐关键信息        │  信息没齐 不准开工
└────────┬─────────────┘
         │  Gate 0: 所有必填项已确认
         ▼
┌──────────────────────┐
│  Step 1: 下载音频    │  yt-dlp 下载音频 (wav格式)
│                      │
└────────┬─────────────┘
         │  Gate 1: 音频文件存在且 > 1KB
         ▼
┌──────────────────────┐
│  Step 2: 语音转文字  │  Whisper 模型转文字
│                      │  输出 SRT 字幕文件
└────────┬─────────────┘
         │  Gate 2: SRT 文件存在且非空
         ▼
┌──────────────────────┐
│  Step 3: 生成笔记    │  理解内容结构
│                      │  提取关键概念 → 结构化输出
└────────┬─────────────┘
         │  Gate 3: 笔记完整（含思维导图+表格）
         ▼
┌──────────────────────┐
│  Step 4: 质量评测    │  确定性评测 + Rubric 评测
│                      │  双维度自动打分验证
└────────┬─────────────┘
         │  Gate 4: 双评测均通过（≥B 或 ≥0.7）
         ▼
┌──────────────────────┐
│  Step 5: 输出与交付  │  按用户指定格式输出
│                      │  Markdown / PDF / Word
└──────────────────────┘
```

## 依赖检查

在开始前，确认以下工具可用：

| 工具 | 用途 | 检查命令 |
|------|------|----------|
| yt-dlp | 下载视频/音频 | `which yt-dlp` |
| whisper | 语音转文字 | `python3 -c "import whisper"` |
| evals | 质量评测 | `ls ./evals/deterministic_grader.py` |

如果缺失：
- yt-dlp: `pip install yt-dlp --break-system-packages`
- whisper: `pip install openai-whisper --break-system-packages`

## Step 0: 前置解析与确认（Inversion 模式）

先自动解析所有可用信息，再向用户做一次性确认。禁止追问用户系统可以自己回答的问题。

### 0.1 自动解析 pipeline

按以下顺序自动收集信息：

| 步骤 | 做什么 | 数据来源 |
|------|--------|---------|
| 1 | 解析 URL 识别来源平台 | URL 域名 |
| 2 | 从用户 prompt 提取输出格式关键词 | 用户的自然语言请求 |
| 3 | 用 `yt-dlp --dump-json` 查询视频元数据 | 视频平台 API |
| 4 | 根据时长自动选定 Whisper 模型 | 上一步结果 |

### 0.2 各字段解析规则

**来源平台** — 从 URL 自动识别：
- `bilibili.com` / `b23.tv` → B站
- `youtube.com` / `youtu.be` → YouTube
- `douyin.com` → 抖音
- 其他 → 对应域名

**输出格式** — 本技能仅输出 Markdown。用户无需指定格式，确认时直接显示 "Markdown"。

**视频语言** — 按平台推断：
- B站 → 中文（默认，极少数英文视频由用户纠正）
- YouTube → 需用 `--dump-json` 检查 `language` 或 `subtitles` 字段
- 其他 → 中文（默认）

**视频时长与模型选择** — 用 `yt-dlp --dump-json` 精确获取：

```
duration < 300s (5min)  → tiny
duration < 900s (15min) → base
duration < 1800s (30min)→ small
duration < 3600s (60min)→ medium
duration >= 3600s       → large
```

### 0.3 一次性确认摘要

所有信息自动收集完成后，输出一份完整摘要请用户确认：

```
━━━ 需求确认 ━━━━━━━━━━━━━━━━━━━━━━━━━━
标题:  {视频标题}
来源:  B站 (自动识别)
时长:  5分00秒 → base 模型
输出:  Markdown (从 prompt 识别)
语言:  中文 (平台默认)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
以上是否正确？如需调整请指出，无误回复 Y 开始处理。
```

### 铁律（务必遵守）

1. **必须展示完整确认页，等用户 Y 才开工**。即使用户重复粘贴 URL，也不得视为已确认。必须输出完整的需求摘要并等待用户明确回复 Y（或"确认""没问题"等肯定表达）。
2. **输出格式固定为 Markdown**，无需用户选择。若用户问到 PDF/Word，告知可用 pandoc 自行转换。
3. **已自动解析的信息不需要再问用户**，直接填入摘要。系统能回答的事绝不问用户。
4. **用户确认前禁止任何下载操作**，包括但不限于：下载音频、创建文件、调用非元数据查询的 API。
5. **确认后只可追问必要缺失项**（如本地文件的时长），不得重新问已确认项。
6. **确认摘要必须直接以自然语言输出**，禁止用 `python3 -c`、`bash -c`、`echo` 或其他代码执行方式打印确认页。画线框使用纯文本字符（━ ┃ ─ │），不依赖任何代码执行。

## 工作目录规范

建议按以下目录组织工作流（可自定义）：

| 目录类型 | 默认路径 | 用途 |
|----------|----------|------|
| 下载文件夹 | `~/download/` | 临时下载的音频/视频文件 |
| 临时文件夹 | `~/temp/` | 中间处理文件（SRT 字幕等） |
| 最终文件 | `~/documents/` | 最终生成的笔记文档 |

> 所有路径均可根据个人习惯调整。`~/download/`、`~/temp/`、`~/documents/` 为默认约定，文中以此为例。

## Step 1: 解析输入并下载

### 输入类型

支持以下输入：

1. **URL** (自动识别平台)
   - B站: `bilibili.com/video/BVxxxxxx` 或 `b23.tv/xxx`
   - YouTube: `youtube.com/watch?v=xxx` 或 `youtu.be/xxx`
   - 抖音/小红书/播客等 yt-dlp 支持的平台

2. **本地文件路径**
   - 视频: `.mp4`, `.mkv`, `.mov`, `.webm`, `.avi`
   - 音频: `.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`

### 下载策略

**对于 URL 输入**：
```bash
# 优先下载音频（更快，更小）
cd ~/download
yt-dlp -x --audio-format wav -o "%(id)s_audio.%(ext)s" "<URL>"

# 如果音频下载失败，下载视频后提取
yt-dlp -f "bestvideo+bestaudio" -o "%(id)s_video.%(ext)s" "<URL>"
```

**对于本地文件**：
- 如果是音频文件：直接使用
- 如果是视频文件：提取音频
  ```bash
  yt-dlp -x --audio-format wav -o "~/download/extracted_audio.%(ext)s" "/path/to/video.mp4"
  ```

### yt-dlp 速查参考

当需要特定格式选择、平台特殊参数、字幕下载、或遇到下载问题时，查阅：
`references/yt-dlp-cheatsheet.md`

### 输出文件命名

- 音频文件: `{视频ID}_audio.wav` 或 `extracted_audio.wav`
- SRT字幕: `{视频ID}_audio.srt`

### Gate 1: 下载完成 → 进入 Step 2

进入 Step 2 前必须逐项确认：

```
□ 音频文件已下载（路径: ~/download/{文件名}.wav）
□ 文件大小 > 1KB（非空文件）
□ 文件格式为 .wav
```

任一条件不满足 → 禁止进入 Step 2，返回诊断下载失败原因。

## Step 2: Whisper 语音转文字

### 模型选择

根据视频长度选择模型：

| 视频长度 | 推荐模型 | 速度 | 准确率 |
|----------|----------|------|--------|
| < 15分钟 | `tiny` | 最快 | 一般 |
| 15-30分钟 | `base` | 快 | 较好 |
| 30-45分钟 | `small` | 中等 | 好 |
| 45-60分钟 | `medium` | 较慢 | 很好 |
| > 60分钟 | `large` | 最慢 | 最好 |

默认使用 `base` 模型（平衡速度和准确率）。

### 执行命令

```bash
cd ~/download
whisper "{audio_file}.wav" --model base --language zh --output_format srt --output_dir .
```

### 语言检测

- 中文视频: `--language zh`
- 英文视频: `--language en`
- 自动检测: 省略 `--language` 参数

### Gate 2: 转录完成 → 进入 Step 3

进入 Step 3 前必须逐项确认：

```
□ SRT 字幕文件已生成（路径: ~/download/{文件名}.srt）
□ 字幕文件非空（总条数 > 0）
□ 字幕语言与 Step 0 中指定的语言一致（若用户指定了语言）
```

任一条件不满足 → 禁止进入 Step 3，返回诊断转录失败原因（模型太小？音频质量差？语言参数错误？）。

## Step 3: 分析内容生成笔记

### 读取 SRT 文件

SRT 格式包含时间戳和文本，用于：
- 理解内容结构
- 定位关键概念的时间点
- 生成章节划分

### 笔记结构模板

生成的笔记必须包含以下部分：

```markdown
# {视频标题} 学习笔记

> 视频来源：{平台} | {视频URL例如:[视频标题](https://www.bilibili.com/video/****)}

---

## 思维导图

{使用 ASCII 或 Mermaid 格式的思维导图，展示整体结构}

---

## 一、{主要章节1}

### 1.1 {子主题}

{详细解释，包含定义、原理、示例}

**时间复杂度对比表**（如适用）：
| 操作 | 数据结构A | 数据结构B |
|------|-----------|-----------|
| 访问 | O(1) | O(n) |

**关键点总结**：
- 要点1
- 要点2

---

## 二、{主要章节2}

...

---

## 六、选择指南

### 6.1 操作复杂度对比

| 数据结构 | 访问 | 搜索 | 插入 | 删除 |
|----------|------|------|------|------|
| {结构A} | O(?) | O(?) | O(?) | O(?) |
| {结构B} | O(?) | O(?) | O(?) | O(?) |

### 6.2 决策树

{使用 ASCII 图形展示何时选择哪种结构}

---

## 七、知识提炼 / Q&A

### 7.1 核心问题

1. {核心问题1}：{解答}
2. {核心问题2}：{解答}
3. ...

### 7.2 关键概念速查

| 概念 | 说明 | 关联知识点 |
|------|------|-----------|
| {概念1} | {简要说明} | {关联内容} |
| {概念2} | {简要说明} | {关联内容} |

---

## 总结

{核心要点回顾}

> **没有最好的数据结构，只有最合适的数据结构。**

{每种结构的适用场景一句话总结}

---

*笔记生成时间：{日期}*
*基于视频：{视频信息}*
```

### 必须包含的元素

1. **思维导图** - 整体结构概览
2. **时间复杂度表** - 性能对比
3. **选择指南/决策树** - 何时使用哪种
4. **知识提炼** - 核心概念速查与 Q&A
5. **代码示例**（如适用）

### Gate 3: 笔记生成完成 → 进入 Step 4

```
□ 笔记内容不为空
□ 包含思维导图（Mermaid 或 ASCII）
□ 包含至少一个表格
□ 文件大小合理（> 1KB）
```

任一条件不满足 → 标记为"质量不合格"，重新生成。

## Step 4: 质量评测

笔记生成后，**必须**运行双评测脚本进行质量打分，结果决定是否交付或需返工。

### 评测命令

```bash
# 确定性评测（7 项检查）
python3 ./evals/deterministic_grader.py ~/documents/{笔记文件}.md

# Rubric 评测（4 维度）
python3 ./evals/rubric_grader.py ~/documents/{笔记文件}.md
```

### 评测标准

| 评测 | 通过线 | 满分 | 说明 |
|------|--------|------|------|
| 确定性评测 | ≥ 0.70 | 1.0 | 7 项硬性检查：文件大小、思维导图、对比内容、选择指南、总结、章节、表格 |
| Rubric 评测 | ≥ 0.65 | 1.0 | 4 维度：完整性 / 结构 / 准确性 / 可复习性 |

### 评测结果处理

```
通过（双通过 ≥ 通过线）
  → 记录成绩，进入 Step 5 交付
  └── deterministic_grader 返回 grade A/B/C/D
  └── rubric_grader 返回 grade A/B/C/D

不通过（任一 < 通过线）
  → 标记"质量不合格"，诊断问题后返回 Step 3 重新生成
  ├── deterministic < 0.70: 查缺失项（缺少章节/表格/思维导图？）
  └── rubric < 0.65: 查弱维度（内容太短？结构混乱？）
```

### Gate 4: 评测通过 → 进入 Step 5

```
□ deterministic_grader score ≥ 0.70（或 grade ≥ B）
□ rubric_grader score ≥ 0.65（或 grade ≥ B）
```

任一条件不满足 → 禁止进入 Step 5，标记"质量不合格"，返回 Step 3 重新生成。

## Step 5: 输出路由与交付

输出固定为 Markdown，直接写入 `~/documents/`：

| 格式 | 路径 | 说明 |
|------|------|------|
| Markdown | `~/documents/{名称}_学习笔记.md` | 唯一内置输出格式 |

> Markdown 以外的格式（PDF、Word 等）请使用 [pandoc](https://pandoc.org/) 自行转换：
> ```bash
> pandoc 笔记.md -o 笔记.docx    # 转 Word
> pandoc 笔记.md -o 笔记.pdf     # 转 PDF（需安装 LaTeX 或 weasyprint）
> ```

### 文件命名

- 使用视频标题或描述性名称
- 格式: `{描述性名称}_学习笔记.md`
- 如：`数据结构详解_学习笔记.md`、`React入门教程_学习笔记.md`

### 交付确认

输出完成后，向用户报告：

```
━━━ 交付完成 ━━━
输出文件: ~/documents/{文件名}
输出格式: {Markdown/PDF/Word}
总耗时:  ~{X}分钟
━━━━━━━━━━━━━━━
```

## 输出质量标准

### 内容标准

1. **完整性**：不遗漏重要知识点
2. **结构性**：逻辑清晰，层次分明
3. **准确性**：技术术语、复杂度分析正确
4. **实用性**：包含选择指南、知识提炼

### 格式标准

1. 使用统一的标题层级
2. 表格对齐美观
3. 代码块有语法高亮
4. 思维导图清晰易读

## 边界情况处理

### 视频无法下载

- 检查网络连接
- 确认 URL 正确
- 高分辨率视频可能需要登录 cookies（提示用户）

### Whisper 转写效果差

- 尝试使用更大的模型（`medium` 或 `large`）
- 检查音频质量
- 对于英文视频，显式指定 `--language en`

### 视频过长（> 60分钟）

- 考虑分段处理
- 使用 `large` 模型提高准确率
- 明确告知用户处理时间较长

### 门控失败

如果 Gate 1/2/3 任一失败，不要跳过，按以下路径处理：

```
Gate 1 失败 (音频下载):
  → 检查网络连接
  → 尝试 yt-dlp 使用 cookies（需登录的视频）
  → 提示用户手动提供 cookies 文件

Gate 2 失败 (字幕为空):
  → 切换到更大模型重新转录
  → 检查语言参数是否正确
  → 如果是纯音频噪音，告知用户

Gate 3 失败 (笔记不完整):
  → 检查 SRT 内容是否过短
  → 重新运行 Step 3 生成
```

### 多语言混合

- 让 Whisper 自动检测语言（省略 `--language`）
- 或分段处理不同语言部分

## 格式转换

本技能仅直接输出 Markdown。如需转换为 PDF、Word 等其他格式，推荐使用 [pandoc](https://pandoc.org/)：

```bash
pandoc note.md -o note.docx    # Markdown → Word
pandoc note.md -o note.pdf     # Markdown → PDF（需 LaTeX 或 weasyprint）
```

### 内置依赖

| 脚本 | 用途 |
|------|------|
| `evals/deterministic_grader.py` | 确定性评测（7 项硬性检查） |
| `evals/rubric_grader.py` | Rubric 评测（4 维度评分） |
| `scripts/check-deps.sh` | 运行时依赖检查 |
| `references/yt-dlp-cheatsheet.md` | yt-dlp 参数速查 |

Step 4 质量评测为本技能的**标准环节**，非可选步骤。

## 快速执行清单

```
□ Step 0: 前置澄清 — 来源/输出格式/语言/长度 四问确认
    └── Gate 0: 必填项已确认
□ Step 1: 下载音频
    └── Gate 1: .wav 存在且 > 1KB
□ Step 2: Whisper 转文字
    └── Gate 2: .srt 存在且非空
□ Step 3: 分析生成笔记
    └── Gate 3: 笔记完整含思维导图+表格
□ Step 4: 质量评测
    ├── deterministic_grader.py (通过线 ≥ 0.70)
    ├── rubric_grader.py (通过线 ≥ 0.65)
    └── Gate 4: 双评测均通过
□ Step 5: 按用户指定格式输出
    └── 交付: ~/documents/{名称}_学习笔记.md
```
