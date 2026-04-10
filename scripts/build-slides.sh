#!/bin/bash
# build-slides.sh — slides.md → PDF/HTML 변환 (Marp CLI 감지형)
# Marp가 설치되어 있으면 자동 변환, 없으면 안내 후 정상 종료
#
# 사용법:
#   ./scripts/build-slides.sh <slides.md>
#
# 예시:
#   ./scripts/build-slides.sh my-project/reports/slides/slides.md

set -euo pipefail

INPUT="${1:?사용법: ./scripts/build-slides.sh <slides.md>}"
OUTPUT_DIR="$(dirname "$INPUT")"

if [ ! -f "$INPUT" ]; then
  echo "❌ 입력 파일이 없습니다: $INPUT"
  exit 1
fi

echo "=== Deep-Briefing 슬라이드 빌드 ==="
echo "  입력: ${INPUT}"
echo ""

# Marp CLI 감지
if command -v marp &>/dev/null || npx @marp-team/marp-cli --version &>/dev/null 2>&1; then
  echo "✅ Marp CLI 감지됨 — 자동 변환 시작"
  echo ""

  # Marp 명령 결정
  if command -v marp &>/dev/null; then
    MARP_CMD="marp"
  else
    MARP_CMD="npx @marp-team/marp-cli"
  fi

  # PDF 생성
  echo "📄 PDF 생성 중..."
  $MARP_CMD "$INPUT" --pdf --allow-local-files -o "${OUTPUT_DIR}/slide-deck.pdf" 2>&1 && \
    echo "  ✅ ${OUTPUT_DIR}/slide-deck.pdf" || \
    echo "  ⚠️  PDF 생성 실패 (Chrome/Chromium 필요)"

  # HTML 생성
  echo "🌐 HTML 생성 중..."
  $MARP_CMD "$INPUT" --html --allow-local-files -o "${OUTPUT_DIR}/slide-deck.html" 2>&1 && \
    echo "  ✅ ${OUTPUT_DIR}/slide-deck.html" || \
    echo "  ⚠️  HTML 생성 실패"

  echo ""
  echo "빌드 완료!"

else
  echo "ℹ️  Marp CLI가 설치되어 있지 않습니다."
  echo ""
  echo "slides.md는 Marp 호환 Markdown입니다."
  echo "다음 방법 중 하나로 슬라이드를 변환할 수 있습니다:"
  echo ""
  echo "  1. Marp CLI (추천):"
  echo "     npx @marp-team/marp-cli ${INPUT} --pdf --html --allow-local-files"
  echo ""
  echo "  2. VS Code 확장:"
  echo "     'Marp for VS Code' 설치 → ${INPUT} 열기 → 미리보기/내보내기"
  echo ""
  echo "  3. Google Slides / PowerPoint:"
  echo "     slides.md의 각 '---' 구분을 슬라이드로 수동 변환"
  echo ""
  echo "  4. reveal.js:"
  echo "     slides.md를 reveal.js Markdown 플러그인으로 로드"
  echo ""
  echo "slides.md 정본 위치: ${INPUT}"
fi
