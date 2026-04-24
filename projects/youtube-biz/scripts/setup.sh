#!/bin/bash
# YouTube Biz 프로젝트 초기 환경 셋업
# 실행: bash scripts/setup.sh

echo "=== YouTube Biz Setup ==="
echo

# Python 의존성 설치
echo "[1] Python 패키지 설치..."
pip install \
  yt-dlp \
  faster-whisper \
  anthropic \
  pyyaml \
  httpx \
  google-api-python-client \
  google-auth-httplib2 \
  google-auth-oauthlib \
  instagrapi

echo

# .env 파일 생성 (없는 경우)
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
if [ ! -f "$SCRIPT_DIR/.env" ]; then
  echo "[2] .env 파일 생성 중..."
  cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
  echo ".env 파일 생성 완료. API 키를 입력해주세요: $SCRIPT_DIR/.env"
else
  echo "[2] .env 파일 이미 존재."
fi

echo

# ffmpeg 확인
echo "[3] ffmpeg 확인..."
if command -v ffmpeg >/dev/null 2>&1; then
  echo "  ffmpeg: $(ffmpeg -version 2>&1 | head -1)"
else
  echo "  [WARN] ffmpeg 미설치."
  echo "  Windows: https://ffmpeg.org/download.html 에서 다운로드 후 PATH에 추가"
fi

echo
echo "셋업 완료. 다음 단계:"
echo "  1. .env 파일에 API 키 입력"
echo "  2. python scripts/run_phase0_smoketest.py"
echo "  3. python pipelines/singit_daily.py --dry-run"
