# yt-dlp 速查参考

## 格式选择

| 要求 | 命令 |
|------|------|
| 最佳质量 | `-f "bestvideo+bestaudio/best"` |
| 4K | `-f "bestvideo[height<=2160]+bestaudio/best"` |
| 1080p | `-f "bestvideo[height<=1080]+bestaudio/best"` |
| 720p | `-f "bestvideo[height<=720]+bestaudio/best"` |
| 480p | `-f "bestvideo[height<=480]+bestaudio/best"` |
| MP4 容器 | `-f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"` |
| 列出所有可用格式 | `yt-dlp -F "<URL>"` |
| 指定格式编号 | `-f 137+140` |
| 指定输出容器 | `--merge-output-format mkv` |

## 平台特殊处理

| 平台 | 注意点 |
|------|--------|
| YouTube | **始终**加 `--cookies-from-browser chrome`，否则返回 HTTP 403 |
| Bilibili | 字幕参数 `--write-subs --sub-langs "zh-Hans"`；高清需 `--cookies-from-browser` |
| TikTok/抖音 | 直接用 URL，无水印版本可能需要额外参数 |
| Twitter/X | 需要 `--cookies-from-browser` 访问受限内容 |
| Instagram | 需要 `--cookies-from-browser` |

Cookies 支持的浏览器：`chrome`, `firefox`, `safari`, `edge`, `brave`, `opera`

## 字幕下载

```bash
# 人工字幕
yt-dlp --write-subs --sub-langs "en,zh" "<URL>"

# 自动生成字幕（如 YouTube）
yt-dlp --write-auto-subs --sub-langs "en" "<URL>"

# 两者都要并嵌入
yt-dlp --write-subs --write-auto-subs --sub-langs "en,zh" --embed-subs "<URL>"

# 查看可用字幕
yt-dlp --list-subs "<URL>"

# 转换为 SRT 格式
yt-dlp --write-subs --sub-format srt "<URL>"
```

## 输出命名模板

| 变量 | 说明 | 示例 |
|------|------|------|
| `%(title)s` | 视频标题 | My Video |
| `%(id)s` | 视频 ID | dQw4w9WgXcQ |
| `%(ext)s` | 扩展名 | mp4 |
| `%(upload_date)s` | 上传日期 | 20231215 |
| `%(uploader)s` | 频道名 | Rick Astley |
| `%(playlist)s` | 播放列表名 | Best Songs |
| `%(playlist_index)s` | 播放列表序号 | 01 |
| `%(resolution)s` | 分辨率 | 1920x1080 |

## 播放列表处理

```bash
# 下载整个播放列表
yt-dlp "PLAYLIST_URL"

# 只下载单集（不展开播放列表）
yt-dlp --no-playlist "<URL>"

# 指定序号（1-indexed）
yt-dlp -I 1:5 "PLAYLIST_URL"        # 前 5
yt-dlp -I 1,3,5 "PLAYLIST_URL"      # 第 1,3,5 集
yt-dlp -I -3: "PLAYLIST_URL"        # 最后 3 集

# 跳过已下载的
yt-dlp --download-archive downloaded.txt "PLAYLIST_URL"
```

## 常见问题

| 问题 | 解决 |
|------|------|
| HTTP 403（YouTube） | 加 `--cookies-from-browser chrome` |
| 下载慢 | 加 `--concurrent-fragments 4` |
| 格式合并失败 | 确认 ffmpeg 已安装 |
| 区域限制 | 加 `--geo-bypass` 或代理 |
| 持续失败 | 更新 yt-dlp `pip install -U yt-dlp` 或强制 IPv4 `-4` |
