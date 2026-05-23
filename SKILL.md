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
│  Step 5: 输出与交付  │  固定输出 Markdown
│                      │  Markdown / PDF / Word
└──────────────────────┘
```

## 依赖检查

需要 `yt-dlp` 和 `openai-whisper`：`which yt-dlp && python3 -c "import whisper"`，缺失则 `pip install ... --break-system-packages`。评测脚本在 `./evals/` 目录。

## Step 0: 前置解析与确认（Inversion 模式）

先自动解析所有可用信息，再向用户做一次性确认。禁止追问用户系统可以自己回答的问题。

### 0.1 自动解析 pipeline

解析 URL 识别平台 → `yt-dlp --dump-json` 查标题/时长 → 按时长选模型。

### 0.2 各字段解析规则

**来源平台**：`bilibili.com`/`b23.tv`→B站, `youtube.com`/`youtu.be`→YouTube, `douyin.com`→抖音, 其他→对应域名。

**视频语言**：B站默认中文，YouTube 检查 `language` 字段，其他默认中文。

**视频时长与模型选择** — 用 `yt-dlp --dump-json` 获取时长，按 Step 2 的模型选择表确定模型。

### 0.3 一次性确认摘要

所有信息自动收集完成后，输出一份完整摘要请用户确认：

```
━━━ 需求确认 ━━━━━━━━━━━━━━━━━━━━━━━━━━
标题:  {视频标题}
来源:  B站 (自动识别)
 时长:  20分00秒 → base 模型
输出:  Markdown (从 prompt 识别)
语言:  中文 (平台默认)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
以上是否正确？如需调整请指出，无误回复 Y 开始处理。
```

### 铁律（务必遵守）

1. **必须展示完整确认页，等用户 Y 才开工**，不得视为已确认。
2. **用户确认前禁止任何下载操作**，包括下载音频、创建文件、调用非元数据 API。
3. **确认摘要用纯文本字符输出**（━ ┃ ─ │），禁止用代码执行画确认页。

## Step 1: 解析输入并下载

### 输入类型

- **URL**：B站 (`bilibili.com` / `b23.tv`)、YouTube (`youtube.com` / `youtu.be`)、抖音等 yt-dlp 支持的所有平台
- **本地文件**：视频 (mp4/mkv/mov/webm/avi)、音频 (mp3/wav/m4a/flac/ogg)

### 下载策略

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

检查 `.wav` 文件存在且 > 1KB，否则诊断重试。

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

中文: `--language zh` / 英文: `--language en` / 留空则自动检测。

### Gate 2: 转录完成 → 进入 Step 3

检查 SRT 文件存在且非空，语言与 Step 0 指定一致，否则诊断重试。

## Step 3: 分析内容生成笔记

读取 SRT 中的时间戳和文本，理解内容结构，定位关键概念，生成章节划分。

### 笔记必须包含

- 标题 + 来源信息
- 思维导图（最好是 Mermaid **mindmap** 格式）
- 章节内容（含对比表/复杂度分析）
- 选择指南 / 决策树
- 知识提炼 / Q&A
- 总结（核心要点回顾）
- 笔记生成时间

### Mermaid mindmap 注意事项

- 使用 `mindmap` 语法（非 `graph TD`）
- 节点文本中含括号 `()` 时，**必须**将整个文本用双引号包裹：`"scanSkills(): 递归扫描"`
- 嵌套结构用缩进表示层级关系
- 根节点可用 `root((text))` 双圆样式

### Gate 3: 笔记生成完成 → 进入 Step 4

检查笔记包含思维导图和至少一个表格，且文件大小合理（>1KB），否则标记不合格重写。

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

双通过 → 进入 Step 5。任一不及格 → 回 Step 3 重写；deterministic 不及格查缺项，rubric 不及格查弱维度。

### Gate 4: 评测通过 → 进入 Step 5

检查双评测成绩均 ≥ 通过线（0.70 / 0.65），任一不满足则回 Step 3 重写。

## Step 5: 输出交付

输出固定为 Markdown，文件名 `{描述性名称}_学习笔记.md`，写入 `~/documents/`。完成后向用户报告文件路径和格式。

> Markdown 以外的格式（PDF、Word 等）请使用 [pandoc](https://pandoc.org/)：`pandoc 笔记.md -o 笔记.docx` / `pandoc 笔记.md -o 笔记.pdf`（需 LaTeX）

## 边界情况处理

下载失败 → 查网络 / 尝试 cookies。转写效果差 → 换大模型 / 检查语言参数。视频超长 → 分段处理 / 用 large。门控失败 → 对应 Step 的诊断重试。






