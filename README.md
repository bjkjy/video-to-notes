# Video to Notes — 视频转学习笔记

将任意视频或音频自动转换为结构化、可复习的学习笔记。

支持 B站、YouTube、抖音、小红书、播客等平台。使用 yt-dlp 下载音频，Whisper 语音转文字，再经 LLM 分析生成带思维导图、对比表格、选择指南、面试考点的专业笔记。

## 功能特性

- **全自动 6 Step 工作流** — 前置确认 → 下载 → 转写 → 生成 → 评测 → 交付
- **Inversion 模式** — 先确认需求再开工，不做无用功
- **智能模型适配** — 根据视频时长自动选择 Whisper 模型（tiny → large）
- **双评测体系** — 确定性评测（7 项硬检查）+ Rubric 评测（4 维度质量评分）
- **门控机制** — 每一阶段都有门控检查，不过关不往下走
- **Markdown 输出** — 默认生成 `.md` 文件，PDF/Word 可借助 pandoc 自行转换

## 快速开始

### 依赖安装

```bash
# yt-dlp — 下载音频
pip install yt-dlp --break-system-packages

# openai-whisper — 语音转文字
pip install openai-whisper --break-system-packages
```

检查依赖：

```bash
bash scripts/check-deps.sh
```

### 使用方式

1. 在 LLM 对话中提供视频 URL，Skill 会自动处理
2. 你只需确认需求摘要，其余全自动

## 工作流概览

```
URL/本地文件 → yt-dlp 下载音频 → Whisper 转文字
  → LLM 生成结构化笔记 → 双评测 → 交付 Markdown
```

每个阶段有严格的门控检查，确保输出质量。

## 内置脚本与评测

| 路径 | 用途 |
|------|------|
| `scripts/check-deps.sh` | 运行时依赖检查 |
| `evals/deterministic_grader.py` | 确定性评测（7 项硬性检查） |
| `evals/rubric_grader.py` | Rubric 评测（4 维度评分） |
| `references/yt-dlp-cheatsheet.md` | yt-dlp 参数速查 |

## 输出示例

生成的笔记包含：

- 思维导图（Mermaid/ASCII）
- 章节化知识点
- 对比表格与复杂度分析
- 选择指南 / 决策树
- 面试高频考点
- 核心要点总结

## 兼容性

### 输入平台

B站、YouTube、抖音、小红书、播客等 yt-dlp 支持的所有平台

### 输入格式

视频：`.mp4` `.mkv` `.mov` `.webm` `.avi`
音频：`.mp3` `.wav` `.m4a` `.flac` `.ogg`

## 许可证

MIT
