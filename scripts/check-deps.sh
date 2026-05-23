#!/usr/bin/env bash
# Detect available tools for video-to-notes skill

echo "=== Video to Notes Dependency Check ==="
echo ""

MISSING=0

if command -v yt-dlp &>/dev/null; then
  YTDLP_VERSION=$(yt-dlp --version 2>/dev/null)
  echo "✓ yt-dlp found: version $YTDLP_VERSION"
else
  echo "✗ yt-dlp NOT found"
  MISSING=1
fi

if python3 -c "import whisper" &>/dev/null 2>&1; then
  WHISPER_VERSION=$(python3 -c "import whisper; print(whisper.__version__)" 2>/dev/null || echo "installed")
  echo "✓ whisper found: version $WHISPER_VERSION"
else
  echo "✗ whisper NOT found"
  MISSING=1
fi

echo ""

if [ $MISSING -eq 0 ]; then
  echo "=== All dependencies satisfied ==="
  echo ""
  echo "Video-to-notes workflow available:"
  echo "  1. Download audio: yt-dlp -x --audio-format wav <URL>"
  echo "  2. Transcribe: whisper <audio.wav> --model base --language zh --output_format srt"
  echo "  3. Analyze SRT and generate structured notes"
  echo ""
  exit 0
else
  echo "=== Missing dependencies ==="
  echo ""
  echo "Install commands:"
  echo "  pip install yt-dlp --break-system-packages"
  echo "  pip install openai-whisper --break-system-packages"
  echo ""
  echo "Note: For WSL2 users, add --cache <your-cache-dir> to npm commands to avoid permission issues"
  exit 1
fi
